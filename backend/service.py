from http import HTTPStatus
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from db_model import User
from dto_model import UserCreateDTO, UserDTO, CustomException, DataToken, LoginDTO
from datetime import timedelta, timezone, datetime
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from database import get_db

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_password_hash(password: str):
    return bcrypt_context.hash(password)


async def verify_password(hashed_password, password) -> bool:
    return bcrypt_context.verify(password, hashed_password)


async def db_get_user_by_email(user_mail: str, db: Session) -> UserDTO:
    result = db.query(User).filter(User.email == user_mail).first()

    if result is None:
        raise CustomException(HTTPStatus.NOT_FOUND, "Not found")

    return UserDTO(id=result.id, email=result.email)


async def db_get_user_by_id(user_id: int, db: Session):
    result = db.query(User).filter(User.id == user_id).first()

    if result is None:
        raise CustomException(HTTPStatus.NOT_FOUND, "Not found")

    return UserDTO(id=result.id, email=result.email)

async def create_user(user: UserCreateDTO, db: Session) -> UserDTO:
    found_user = db.query(User).filter(User.email == user.email).first()

    if found_user is not None:
        raise CustomException(HTTPStatus.NOT_FOUND, f"User with email {user.email} already")

    hashed_password = await get_password_hash(user.password)

    db_user = User(email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return UserDTO(id=db_user.id, email=db_user.email)


async def db_delete_user_by_id(user_id: int, db: Session):
    user = db_get_user_by_id(user_id, db)

    db.delete(user)
    db.commit()


async def user_verification(login_data: LoginDTO, db: Session) -> UserDTO:
    user_from_db = db.query(User).filter(User.email == login_data.email).first()

    if user_from_db is None:
        raise CustomException(HTTPStatus.NOT_FOUND, "User not found")

    if not  verify_password(user_from_db.password, login_data.password):
        raise CustomException(HTTPStatus.UNAUTHORIZED, "Incorrect password")

    return UserDTO(id=user_from_db.id, email=user_from_db.email)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


async def create_access_token(user: UserDTO):
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    token_data = {"user_id": user.id, "user_mail": user.email, "expire": expire.strftime("%Y-%m-%d %H:%M:%S")}

    encoded_jwt = jwt.encode(token_data, SECRET_KEY, ALGORITHM)

    return encoded_jwt


def verify_token_access(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)

        id: str = payload.get("user_id")

        if id is None:
            raise credentials_exception
        token_data = DataToken(id=id)
    except JWTError as e:
        print(e)
        raise credentials_exception

    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not Validate Credentials",
                                          headers={"WWW-Authenticate": "Bearer"})

    token = verify_token_access(token, credentials_exception)
    user = db.query(User).filter(User.id == token.id).first()

    return user


async def login_user_token(login_data: LoginDTO, db: Session = Depends(get_db)):
    user = await user_verification(login_data, db)
    return await create_access_token(user)

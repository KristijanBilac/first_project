from datetime import timedelta, timezone, datetime, time
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from database import get_db
from dto_model import UserDTO, DataToken, LoginDTO
from db_model import User
from service import user_verification

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


async def create_access_token(user: UserDTO):

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    token_data = {"user_id": user.id,
                  "user_mail": user.email,
                   "expire": expire.strftime("%Y-%m-%d %H:%M:%S")
                  }

    encoded_jwt_token= jwt.encode(token_data, SECRET_KEY, ALGORITHM)

    return encoded_jwt_token


def verify_token_access(token: str, credentials_exception: HTTPException):
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

def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return decoded_token
        # return decoded_token if decoded_token["expire"] >= datetime.now(timezone.utc) else None
    except:
        return {}
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

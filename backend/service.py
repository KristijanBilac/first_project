from http import HTTPStatus
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from db_model import User
from dto_model import UserCreateDTO, UserDTO, CustomException, LoginDTO, NewPassword
from fastapi import Depends

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

    if not await verify_password(user_from_db.password, login_data.password):
        raise CustomException(HTTPStatus.UNAUTHORIZED, "Incorrect password")

    return UserDTO(id=user_from_db.id, email=user_from_db.email)


def get_list_of_users(db: Session = Depends()):
    return db.query(User).all()


async def db_update_user_password(user_id: int, new_password: NewPassword, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if user is not None:
        if new_password is not None:
            hashed_password = await get_password_hash(new_password.new_password)
            user.password = hashed_password

            db.commit()
    else:
        raise CustomException(HTTPStatus.NOT_FOUND, "User not found")

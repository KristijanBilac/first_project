from datetime import timedelta, datetime, timezone

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from auth_bearer import JWTBearer
from database import get_db
from service import create_user, db_get_user_by_id, db_get_user_by_email, db_delete_user_by_id, get_list_of_users
from auth_handler import login_user_token
from dto_model import UserCreateDTO, UserDTO, LoginDTO

router = APIRouter()


@router.post("/api/auth/sign-up", response_model=UserDTO, tags=["web"])
async def register_user(user: UserCreateDTO, db: Session = Depends(get_db)):
    return await create_user(user, db)


@router.post("/api/user/login", tags=["web"])
async def login(login_data: LoginDTO, db: Session = Depends(get_db)):
    access_token = await login_user_token(login_data, db)
    return {"access_token": access_token, "token_type": "bearer"}


# @router.get("/api/user/home", dependencies=[Depends(JWTBearer())],tags=["token"])
# def  home(db: Session = Depends(get_db)):
#     users= get_list_of_users(db)
#     return users

@router.post("/cookie-and-object/")
async def create_cookie(response: Response, login_data: LoginDTO, db: Session = Depends(get_db)):
    access_token = await login_user_token(login_data, db)
    response.set_cookie(key="session_token", value=f"Bearer {access_token}", expires=3600)
    return {"acces token": f"{access_token}"}


@router.get("/api/user/{id}", response_model=UserDTO, tags=["test"])
async def read_user(user_id: int, db: Session = Depends(get_db)):
    return await db_get_user_by_id(user_id, db)


@router.get("/api/user/mail", response_model=UserDTO, tags=["test"])
async def read_user_mail(user_mail: str, db: Session = Depends(get_db)):
    return await db_get_user_by_email(user_mail, db)


@router.delete("/api/user/delete/id", tags=["test"])
async def delete_user_by_id(user_id: int, db: Session = Depends(get_db)):
    await db_delete_user_by_id(user_id, db)
    return {"result": True}

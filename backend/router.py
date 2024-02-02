from datetime import timedelta, datetime, timezone

from fastapi import APIRouter, Depends, Response, Form
from sqlalchemy.orm import Session
from database import get_db
from service import create_user, db_get_user_by_id, db_get_user_by_email, db_delete_user_by_id, get_list_of_users,db_update_user_password
from auth_handler import login_user_token, decodeJWT, get_token
from dto_model import UserCreateDTO, UserDTO, LoginDTO, NewPassword

router = APIRouter()


@router.post("/api/auth/sign-up", response_model=UserDTO, tags=["web"])
async def register_user(user: UserCreateDTO, db: Session = Depends(get_db)):
    return await create_user(user, db)


@router.post("/api/user/login", tags=["web"])
async def login(response: Response, login_data: LoginDTO, db: Session = Depends(get_db)):
    access_token = await login_user_token(login_data, db)
    response.set_cookie(key="session_token", value=f"Bearer {access_token}", expires=3600)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/api/user/home",tags=["web"])
def home(token: str = Depends(get_token),db: Session = Depends(get_db)):
    decode_token = decodeJWT(token)
    users = get_list_of_users(db)
    return users


@router.patch("/api/user/update", tags=["web"])
async def update_user(new_password: NewPassword, token: str = Depends(get_token), db: Session = Depends(get_db)):
    print(f"---------------------1------------")
    decoded_token = decodeJWT(token)
    print(f"---------------------2------------")
    user = await db_get_user_by_id(decoded_token.get("user_id"), db)
    print(f"-----------------------3----------User:{user}")
    print(f"-----------------------4----------New Password: {new_password}")
    await db_update_user_password(user.id, new_password, db)
    print(f"---------------------5------------")
    return user



# @router.get("/api/user/home", dependencies=[Depends(JWTBearer())],tags=["token"])
# def  home(db: Session = Depends(get_db)):
#     users= get_list_of_users(db)
#     return users

# @router.post("/cookie-and-object/")
# async def create_cookie(response: Response, login_data: LoginDTO, db: Session = Depends(get_db)):
#     access_token = await login_user_token(login_data, db)
#     response.set_cookie(key="session_token", value=f"Bearer {access_token}", expires=3600)
#     return {"acces token": f"{access_token}"}


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

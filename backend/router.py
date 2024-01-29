from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from service import create_user, db_get_user_by_id, db_get_user_by_email, db_delete_user_by_id, user_verification, \
    create_access_token, get_password_hash, login_user_token
from dto_model import UserCreateDTO, UserDTO, CustomException, LoginDTO
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post("/api/auth/sign-up", response_model=UserDTO)
async def register_user(user: UserCreateDTO, db: Session = Depends(get_db)):
    return await create_user(user, db)


@router.post("/api/user/login")
async def login(login_data: LoginDTO, db: Session = Depends(get_db)):
    access_token = await login_user_token(login_data, db)
    return {"access_token": access_token, "token_type": "bearer"}

# @router.post("/api/user/home")
# def home(userdetails: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     user = db_get_user_by_email(userdetails.username,db)
#     user_verification(userdetails,db)
#     access_token = create_access_token(data={"user_id": user.id})
#     return {"access_token": access_token, "token_type": "bearer"}


@router.get("/api/user/{id}", response_model=UserDTO)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    return await db_get_user_by_id(user_id, db)


@router.get("/api/user/mail", response_model=UserDTO)
async def read_user_mail(user_mail: str, db: Session = Depends(get_db)):
    return await db_get_user_by_email(user_mail, db)


@router.delete("/api/user/delete/id")
async def delete_user_by_id(user_id: int, db: Session = Depends(get_db)):
    await db_delete_user_by_id(user_id, db)
    return {"result": True}

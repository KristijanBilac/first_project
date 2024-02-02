from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    detail: str
    status_code: int


class UserCreateDTO(BaseModel):
    email: str
    password: str


class UserDTO(BaseModel):
    id: int
    email: str

class LoginDTO(BaseModel):
    email: str
    password: str

class NewPassword(BaseModel):
    new_password: str


class CustomException(HTTPException):
    def __init__(self, status_code, detail: str):
        super().__init__(status_code=status_code, detail=detail)



class Token(BaseModel):
    access_token: str
    token_type:str

class DataToken(BaseModel):
    id:Optional[str] = None

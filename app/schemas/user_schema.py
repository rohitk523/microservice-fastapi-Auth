# app/schemas/user_schema.py
from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    username: str
    email: str | None = None

    class Config:
        orm_mode = True
        from_attributes = True  # For Pydantic v2 compatibility

class User(BaseModel):
    username: str
    email: Optional[str] = None

class UserInDB(User):
    hashed_password: str
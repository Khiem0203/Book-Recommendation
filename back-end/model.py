from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel, constr, field_validator
import re

Base = declarative_base()

class UserInDB(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))

class FavoriteInDB(Base):
    __tablename__ = 'favorites'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    book_id = Column(String)

class RegisterUser(BaseModel):
    username: constr(max_length=49)
    email: constr(min_length=1)
    password: constr(min_length=8, max_length=15)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z0-9]).+$'
        if not re.match(pattern, v):
            raise ValueError("Password must contain at least one lowercase letter, one uppercase letter, one number, and one special character.")
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if " " in v:
            raise ValueError("Username must not contain spaces.")
        return v

class Favorite(BaseModel):
    book_id: str

class User(BaseModel):
    identifier: str
    password: str

class TokenData(BaseModel):
    username: str | None = None

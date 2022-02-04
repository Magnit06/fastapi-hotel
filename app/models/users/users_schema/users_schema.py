from enum import Enum

from pydantic import BaseModel


class Role(str, Enum):
    admin = "A"
    manager = "M"


class UserBase(BaseModel):
    login: str
    role: Role = Role.manager.value

    class Config:
        use_enum_values = True
        orm_mode = True


class UserCreate(UserBase):
    password: str


class UserSchema(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    login: str
    password: str


class UserToken(BaseModel):
    token: str


class UserAddManagerBase(BaseModel):
    login: str
    role: Role = Role.manager.value

    class Config:
        use_enum_values = True


class UserAddManagerCreate(UserAddManagerBase):
    password: str
    token: str


class UserAddManagerSchema(UserAddManagerBase):
    id: int

    class Config:
        orm_mode = True

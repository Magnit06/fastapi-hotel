from sqlalchemy import (Column, String,
                        Integer, Unicode)
from sqlalchemy.dialects.postgresql import ENUM
from bcrypt import gensalt, hashpw, checkpw

from app.models.base import Base, TimeCheckInterface


class User(Base, TimeCheckInterface):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    login = Column(String(20), nullable=False, unique=True, comment="Логин пользователя")
    _password = Column("password", Unicode(length=60), nullable=False,
                       comment="Пароль пользователя")
    role = Column(ENUM("A", "M", name="Роль"), nullable=False,
                  comment="Роль пользователя")

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, raw_password: str) -> None:
        self._password = self.generate_password(raw_password=raw_password)

    @staticmethod
    def generate_password(raw_password: str) -> str:
        return hashpw(raw_password.encode(), gensalt()).decode()

    def check_password(self, inp_passwd: str) -> bool:
        return checkpw(inp_passwd.encode(), self.password.encode())

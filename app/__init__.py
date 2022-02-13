from os import system

from fastapi import FastAPI

app = FastAPI(title="Hotel")

# from app.models.users.users_schema import UserSchema, UserCreate
from app.views import *


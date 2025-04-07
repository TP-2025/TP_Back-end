from pydantic import BaseModel
from enum import Enum
from typing import Optional


class Patient(BaseModel):
    name: str
    surname: str
    email: str

class UserCreate(Patient):
    user_id: int
    password: str

class UserCheck(Patient):
    user_id: int

class UserLoginRequest(BaseModel):
    email: str
    password: str



#Can be removed

from pydantic import BaseModel
from enum import Enum
from typing import Optional

class UserRole(str, Enum):
    admin = "admin"
    doctor = "doctor"
    technician = "technician"

class User(BaseModel):
    full_name: str
    email: str
    role: UserRole

class UserCreate(User):
    user_id: int
    password: str

class UserCheck(User):
    user_id: int
    role: UserRole

class UserLoginRequest(BaseModel):
    email: str
    password: str
    role: UserRole


get_user()


    return basic_user_info


get_user_detailed()


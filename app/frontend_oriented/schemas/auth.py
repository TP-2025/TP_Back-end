from pydantic import BaseModel, EmailStr
from typing import Optional, List

class LoginRequest(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: str
    email: str
    role_id: int
    role: str

class LoginResponse(BaseModel):
    message: str
    user: Optional[UserOut] = None


class TokenResponse(BaseModel):
    access_token: str

class AdminOut(BaseModel):
    name: str
    surname: str
    email: EmailStr
    id: int

class DoctorOut(BaseModel):
    name: str
    surname: str
    email: EmailStr
    id: int

class GetAdminResponse(BaseModel):
    admins: List[AdminOut]

class GetDoctorResponse(BaseModel):
    doctors: List[DoctorOut]

class CreateUser(BaseModel):
    name: str
    surname: str
    email: EmailStr

class DeleteUser(BaseModel):
    id: int

class ChangePassword(BaseModel):
    password: str
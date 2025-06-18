from typing import Union
from urllib.request import Request

from passlib.context import CryptContext
import uuid
from app.database_oriented.users.user import User

from fastapi import Request, HTTPException, Depends

from app.frontend_oriented.services.token_service import TokenService
token_service = TokenService()


from app.database_oriented.users.admin import Admin
from app.database_oriented.users.medic import Medic
from app.database_oriented.users.patient import Patient
from app.database_oriented.users.technic import Technic

import secrets
import string


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_password(length: int = 7) -> str:
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
    #if plain_password == hashed_password:
    #    return True
    #return False

def authenticate_user(email: str, password: str):
    user = User.get_user_basic_info_by_email(email)

    if not user or not verify_password(password, user['hashed_password']):
        return None
    return user

def check_user(request: Request) -> Union[Admin, Medic, Technic, Patient]:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    payload = token_service.verify_access_token(token)
    role_id = payload.get("role_id")
    user_id = payload.get("user_id")

    match role_id:
        case 1: return Patient(ID=user_id, token=token)
        case 2: return Technic(ID=user_id, token=token)
        case 3: return Medic(ID=user_id, token=token)
        case 4: return Admin(ID=user_id, token=token)
        case _: raise HTTPException(403, "Invalid role")

def mask_name(name: str) -> str:
    if not name:
        return ""
    return name[0] + "*" * (len(name) - 1)
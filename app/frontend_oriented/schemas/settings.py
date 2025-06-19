from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from enum import Enum

from typing import Optional, List

from app.frontend_oriented.schemas.user import SexEnum


class AddDevice(BaseModel):
    name: str
    type: str

class Camera(BaseModel):
    id: int
    name: str
    type: str

class GetDevicesResponse(BaseModel):
    devices: List[Camera]

class ChangePassword(BaseModel):
    email: str
    old_password: str
    new_password: str

class ChangePersonalInfo(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    birth_date: Optional[str] = None
    sex: Optional[SexEnum] = None

class Diagnoses(BaseModel):
    id: Optional[int] = None
    name: str

class GetDiagnoseResponse(BaseModel):
    diagnoses: List[Diagnoses]
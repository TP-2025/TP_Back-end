from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from enum import Enum

from typing import Optional, List

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
    birth_date: Optional[date] = None
    sex: Optional[str] = None

class Diagnoses(BaseModel):
    id: Optional[int] = None
    name: str

class GetDiagnoseResponse(BaseModel):
    diagnoses: List[Diagnoses]
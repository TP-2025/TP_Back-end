from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from enum import Enum

from typing import Optional, List

from app.frontend_oriented.schemas.user import SexEnum


class DeviceBase(BaseModel):
    name: str
    type: str

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(DeviceBase):
    id: int

class DeviceDelete(BaseModel):
    id: int

class DeviceOut(DeviceBase):
    id: int

class GetDevices(BaseModel):
    devices: List[DeviceOut]


class AdditionalDeviceBase(BaseModel):
    name: str

class AdditionalDeviceCreate(AdditionalDeviceBase):
    pass

class AdditionalDeviceUpdate(AdditionalDeviceBase):
    id: int

class AdditionalDeviceDelete(BaseModel):
    id: int

class AdditionalDeviceOut(AdditionalDeviceBase):
    id: int

class GetAdditionalDevices(BaseModel):
    devices: List[AdditionalDeviceOut]


class DiagnoseBase(BaseModel):
    name: str

class DiagnoseCreate(DiagnoseBase):
    pass

class DiagnoseUpdate(DiagnoseBase):
    id: int

class DiagnoseDelete(BaseModel):
    id: int

class DiagnoseOut(DiagnoseBase):
    id: int

class GetDiagnoses(BaseModel):
    diagnoses: List[DiagnoseOut]


class MethodBase(BaseModel):
    name: str

class MethodCreate(MethodBase):
    pass

class MethodUpdate(MethodBase):
    id: int

class MethodDelete(BaseModel):
    id: int

class MethodOut(MethodBase):
    id: int

class GetMethods(BaseModel):
    methods: List[MethodOut]






class ChangePassword(BaseModel):
    email: str
    old_password: str
    new_password: str

class ChangePersonalInfo(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    birth_date: Optional[str] = None
    sex: Optional[SexEnum] = None


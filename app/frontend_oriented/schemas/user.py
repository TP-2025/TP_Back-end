from datetime import date

from pydantic import BaseModel
from enum import Enum
from typing import Optional, List


class CreatePatient(BaseModel):
    name: str
    surname: str
    email: str
    doctor_id: int
    birth_date: Optional[date]
    sex: Optional[str]

class CreateTechnic(BaseModel):
    name: str
    surname: str
    email: str

class PatientOut(BaseModel):
    name: str
    surname: str
    email: str
    patient_id: int
    medic_id: int
    birth_date: date
    sex: str

class GetPatientResponse(BaseModel):
    patients: List[PatientOut]

class DeletePatient(BaseModel):
    id: int

class UserOut(BaseModel):
    name: str
    surname: str
    email: str
    id: int

class UserOutDate(UserOut):
    date: Optional[date]

class GetUsersResponse(BaseModel):
    users: List[UserOut]


from typing import Generic, TypeVar, Optional
from pydantic.generics import GenericModel

T = TypeVar("T")

class APIResponse(GenericModel, Generic[T]):
    success: bool
    code: str
    data: Optional[T]






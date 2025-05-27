from pydantic import BaseModel, EmailStr
from typing import Optional, List

class TechnicOut(BaseModel):
    name: str
    surname: str
    email: EmailStr
    id: int

class GetTechnicResponse(BaseModel):
    technics: List[TechnicOut]

class PatientOut(BaseModel):
    name: str
    surname: str
    email: EmailStr
    id: int
    year_of_birth: int
    sex: str

class GetPatientResponse(BaseModel):
    patients: List[PatientOut]

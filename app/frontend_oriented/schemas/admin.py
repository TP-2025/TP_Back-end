from pydantic import BaseModel, EmailStr
from typing import Optional, List

class TechnicOut(BaseModel):
    name: str
    surname: str
    email: EmailStr
    id: int

class GetTechnicResponse(BaseModel):
    technics: List[TechnicOut]


from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from enum import Enum

class OriginalPictureOut(BaseModel):
    id: int
    path: str
    patient_id: int
    quality: Optional[str] = None
    eye: Optional[str] = None
    technic_notes: Optional[str] = None
    diagnosis_notes: Optional[str] = None
    device_id: Optional[int] = None
    additional_device_id: Optional[int] = None
    date: Optional[str] = None
    technic_id: Optional[int] = None

class GetOriginalPictures(BaseModel):
    pictures: List[OriginalPictureOut]


class QualityEnum(str, Enum):
    Dobra = "Dobra"
    Zla = "Zla"

class EyeEnum(str, Enum):
    l = "l"
    r = "r"

class AddPicture(BaseModel):
    patient_id: int
    device_id: Optional[int] = None
    additional_equipment_id: Optional[int] = None
    quality: Optional[QualityEnum] = None
    technic_notes: Optional[str] = None
    eye: Optional[EyeEnum] = None
    date: Optional[date] = None
    technician_id: Optional[int] = None

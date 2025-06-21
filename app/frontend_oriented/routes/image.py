from typing import Optional, Union

from cffi.model import qualify
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Request, Body, Form
from datetime import datetime

from app.database_oriented.exitcodes_errors import ExitCodes
from app.database_oriented.models.modelimages.model_original_image import ModelOriginalImage
from app.database_oriented.users.admin import Admin
from app.database_oriented.users.medic import Medic
from app.database_oriented.users.technic import Technic
import app.database_oriented.keywords as kw

from app.frontend_oriented.services.auth import check_rights
from app.frontend_oriented.services.image_service import save_upload_file
from app.frontend_oriented.utils.responses import ErrorErroor
from app.frontend_oriented.schemas.image import EyeEnum, QualityEnum, OriginalPictureOut, GetOriginalPictures

router = APIRouter()

@router.post("/addPicture", status_code=201)
async def add_picture(
    patient_id: int = Form(...),
    device_id: Optional[int] = Form(None),
    additional_equipment_id: Optional[int] = Form(None),
    quality: Optional[QualityEnum] = Form(None),
    technic_notes: Optional[str] = Form(None),
    eye: EyeEnum = Form(...),
    date: Optional[str] = Form(None),
    technician_id: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    _: Union[Admin, Medic, Technic] = Depends(check_rights("add_picture")),
):


    def debug_print_form_data(**kwargs):
        print("🧪 DEBUG: Received form data:")
        for key, value in kwargs.items():
            print(f"  {key}: {value}")

    debug_print_form_data(
        patient_id=patient_id,
        device_id=device_id,
        additional_equipment_id=additional_equipment_id,
        quality=quality,
        technic_notes=technic_notes,
        eye=eye,
        date=date,
        technician_id=technician_id
    )

    saved_path = await save_upload_file(
    upload_file=image,
    patient_id=patient_id,
    eye=eye,
    date=date
)

    iso_date = None
    if date:
        try:
            parsed_date = datetime.strptime(date, "%d.%m.%Y")
            iso_date = parsed_date.date()  # ⬅️ TOTO je to, čo databáza očakáva (nie string)
        except ValueError:
            raise ErrorErroor(error="invalid_date_format")

    image_data = {
        kw.KW_IMAGE_PATH: saved_path,
        kw.KW_PATIENT_ID: patient_id,
        "zariadenie_id": device_id,
        "id_pridavneho_zariadenia": additional_equipment_id,
        kw.KW_IMAGE_QUALITY: quality,
        kw.KW_IMAGE_EYE: eye,
        kw.KW_IMAGE_NOTE_TECHNIC: technic_notes,
        "datum_snimania": iso_date,
        kw.KW_IMAGE_TECHNIC_ID: technician_id,
    }

    exit_code, model_image = ModelOriginalImage.add_original_image(image_data)

    if exit_code != ExitCodes.SUCCESS:
        raise ErrorErroor(error="failed_to_add_original_image") #Error500 ?

    return {"message": "original_image_added"}

@router.get("/getOriginalPictures", response_model=GetOriginalPictures)
def get_original_images(
    current_user: Union[Admin, Medic, Technic] = Depends(check_rights("get_original_pictures"))
):

    images = current_user.get_original_images()

    image_response = [
        OriginalPictureOut(
        id=image["id"],
        patient_id=image["pacient_id"],
        path=f"/{image['cesta_k_suboru']}",
        quality=image["kvalita"],
        eye=image["oko"],
        technic_notes=image["technicke_pozn"],
        diagnostic_notes=image["diagnosticke_pozn"],
        device_id=image["zariadenie_id"],
        additional_device_id=image["id_pridavneho_zariadenia"],
        date=image["datum_snimania"].isoformat() if image["datum_snimania"] else None,
        technic_id=image["technik_id"]
        )
        for image in images
    ]

    return GetOriginalPictures(pictures=image_response)

@router.post("/sendForProcessing", status_code=201)
async def send_for_processing(
    current_user: Union[Admin, Medic, Technic] = Depends(check_rights("send_for_processing"))
):
    current_user.send_original_image_for_processing()
    return {"message": "send_for_processing"}

@router.get("/getProcessedImages")
def get_processed_images(
    current_user: Union[Admin, Medic, Technic] = Depends(check_rights("get_processed_pictures"))
):
    current_user.get_processed_images()

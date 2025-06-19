import logging
from datetime import datetime
from datetime import date

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Request, Body
from fastapi.exceptions import RequestValidationError

from app.database_oriented.exitcodes_errors import InvalidTargetRoleError, ExitCodes
from app.database_oriented.others.devices import Device
from app.database_oriented.others.diagnoses import Diagnose
from app.database_oriented.users.medic import Medic
from app.database_oriented.users.technic import Technic
from app.frontend_oriented.schemas.admin import GetPatientResponse
from app.frontend_oriented.schemas.image import AddPicture, QualityEnum, EyeEnum
from app.frontend_oriented.schemas.settings import AddDevice, GetDevicesResponse, Camera, GetDiagnoseResponse, Diagnoses
from app.frontend_oriented.schemas.user import CreatePatient, CreateTechnic, PatientOut, GetPatientResponse, \
    DeletePatient, GetUsersResponse, UserOut, UserOutPersonal
from app.frontend_oriented.services.auth import check_user, create_password, hash_password
from app.frontend_oriented.services.image_service import save_upload_file
from app.frontend_oriented.services.token_service import TokenService
import app.database_oriented.keywords as kw

from app.database_oriented.users.admin import Admin

from app.frontend_oriented.services.email import EmailService


EmailService = EmailService()

router = APIRouter()
token_service = TokenService()


@router.post("/addPatient")
def create_patient(user_data: CreatePatient, current_user=Depends(check_user)):
    if not isinstance(current_user, (Admin, Medic, Technic)):
        raise HTTPException(status_code=403, detail= "Fuck off")

    password = create_password(7)
    hashed_password = hash_password(password)

    user_dict = {
        "meno": user_data.name,
        "priezvisko": user_data.surname,
        "email": user_data.email,
        "lekar_id": user_data.doctor_id,
        "datum_narodenia": user_data.birth_date.strftime("%d.%m.%Y") if user_data.birth_date else None,
        #"rok_narodenia": user_data.birth_date.year if user_data.birth_date else None,
        "pohlavie": user_data.sex
    }

    try:
        exit_code = current_user.add_user(kw.ROLE_PATIENT, user_dict, hashed_password)
        if exit_code != 0:
            raise HTTPException(status_code=400, detail=f"Failed to create user. Exit code: {exit_code}")
        patient_model = current_user.selected_user
    except (PermissionError, InvalidTargetRoleError) as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    #try:
    #    EmailService.send_password_email(str(user_data.email), user_data.name, password)
    #except Exception as e:
    #    raise HTTPException(status_code=500, detail=f"Failed to create doctor: {str(e)}")

    return {"patient_id": patient_model.ID}


@router.post("/addTechnic")
def create_technic(user_data: CreateTechnic, current_user=Depends(check_user)):
    if not isinstance(current_user, Medic):
        raise HTTPException(status_code=403, detail="Fuck off")

    password = create_password(7)
    hashed_password = hash_password(password)

    user_dict = {
        "meno": user_data.name,
        "priezvisko": user_data.surname,
        "email": user_data.email
    }

    try:
        exit_code = current_user.add_user(kw.ROLE_TECHNIC, user_dict, hashed_password)
        if exit_code != 0:
            raise HTTPException(status_code=400, detail=f"Failed to create user. Exit code: {exit_code}")
        technic_model = current_user.selected_user
    except (PermissionError, InvalidTargetRoleError) as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    try:
        EmailService.send_password_email(str(user_data.email), user_data.name, password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create doctor: {str(e)}")

    return {"technic_id": technic_model.ID}

@router.get("/getPatients", response_model=GetPatientResponse)
def get_patients(current_user=Depends(check_user)):
    if not isinstance(current_user, (Medic, Technic)): #TODO: Potereba zistiť čo môže vidieť technik
        raise HTTPException(status_code=403, detail="Fuck off")

    patients = current_user.get_patients()


    user_responses = [
        PatientOut(
            name=patient["meno"],
            surname=patient["priezvisko"],
            email=patient["email"],
            patient_id=patient["id"],
            medic_id = patient["lekar_id"],
            birth_date = datetime.strptime(f"{patient['datum_narodenia']}.{patient['rok_narodenia']}", "%d.%m.%Y").date(),
            sex = patient["pohlavie"]
        )
        for patient in patients
    ]
    return GetPatientResponse(patients=user_responses)


@router.get("/getUsers", response_model=GetUsersResponse)
def get_users(current_user=Depends(check_user)):
    if not isinstance(current_user, (Medic, Technic)):
        raise HTTPException(status_code=403, detail="Fuck off")

    if isinstance(current_user, Medic):
        users = current_user.get_technics()
    elif isinstance(current_user, Technic):
        users = current_user.get_medics()

    user_responses = [
        UserOut(
            name=user["meno"],
            surname=user["priezvisko"],
            email=user["email"],
            id=user["id"]
        )
        for user in users
    ]

    return GetUsersResponse(users=user_responses)





@router.delete("/deletePatient")
def delete_patient(user_data: DeletePatient, current_user=Depends(check_user)):
    if not isinstance(current_user, (Medic, Technic)):
        raise HTTPException(status_code=403, detail="Fuck off")

    #TODO: Skontrolovať či doktor maže vlastného pacienta

    try:
        current_user.delete_user_by_id(user_data.id)
    except (PermissionError) as e:
        raise HTTPException(status_code=403, detail=str(e))



    #Kód na pridanie fotky..
from fastapi import Form
from typing import Optional



@router.post("/addPicture", status_code=201)
async def add_picture(
    patient_id: int = Form(...),
    device_id: Optional[int] = Form(None),
    additional_equipment_id: Optional[int] = Form(None),
    quality: Optional[QualityEnum] = Form(None),
    technic_notes: Optional[str] = Form(None),
    eye: Optional[EyeEnum] = Form(None),
    date: Optional[date] = Form(None),
    technician_id: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user=Depends(check_user),
):
    # Autorizácia
    if not isinstance(current_user, (Admin, Medic, Technic)):
        raise HTTPException(status_code=403, detail="Forbidden")

    # Ulož obrázok
    saved_path = await save_upload_file(image)

    from app.database_oriented.keywords import (
        KW_IMAGE_PATH, KW_PATIENT_ID, KW_DEVICE_ID, KW_IMAGE_QUALITY, KW_IMAGE_EYE,
        KW_IMAGE_NOTE_TECHNIC, KW_IMAGE_DATE, KW_IMAGE_TECHNIC_ID
    )

    image_data = {
        KW_IMAGE_PATH: saved_path,
        KW_PATIENT_ID: patient_id,
        KW_DEVICE_ID: device_id if device_id is not None else kw.V_EMPTY_INT,
        #KW_ADDITIONAL_EQUIPMENT_ID: additional_equipment_id if additional_equipment_id is not None else kw.V_EMPTY_INT,
        KW_IMAGE_QUALITY: quality if quality is not None else kw.V_EMPTY_STRING,
        KW_IMAGE_EYE: eye if eye is not None else kw.V_EMPTY_STRING,
        KW_IMAGE_NOTE_TECHNIC: technic_notes if technic_notes is not None else kw.V_EMPTY_STRING,
        KW_IMAGE_DATE: date if date is not None else kw.V_EMPTY_STRING,
        KW_IMAGE_TECHNIC_ID: technician_id if technician_id is not None else kw.V_EMPTY_INT,
    }
    from app.database_oriented.models.modelimages.model_original_image import ModelOriginalImage

    exit_code, model_image = ModelOriginalImage.add_original_image(image_data)

    if exit_code != ExitCodes.SUCCESS:
        raise HTTPException(status_code=500, detail="Failed to add image")

    return {"filename"}

"""

@router.post("/addPicture", status_code=201)
async def add_picture(
        patient_id: int = Form(...),
        device_id: Optional[int] = Form(None),
        additional_equipment_id: Optional[int] = Form(None),
        quality: Optional[QualityEnum] = Form(None),
        technic_notes: Optional[str] = Form(None),
        eye: Optional[EyeEnum] = Form(None),
        date: Optional[date] = Form(None),
        technician_id: Optional[int] = Form(None),
        image: UploadFile = File(...),  # image je povinný, nie Optional
        current_user=Depends(check_user),
):
    # Tu daj aspoň nejaký print/debug
    print(f"Got upload from patient_id={patient_id} by user={current_user}")

    # Pre jednoduché testovanie - načítaj aspoň header obrázka
    content = await image.read()
    print(f"Image size: {len(content)} bytes, filename={image.filename}")

    # Tu môžeš uložiť obrázok a spracovať metadáta
    # ...

    return {"message": "Image uploaded successfully", "patient_id": patient_id}

"""

@router.post("/addDevice", status_code=201)
def add_device(device_data: AddDevice,current_user=Depends(check_user)):
    if not isinstance(current_user, (Admin, Medic, Technic)):
        raise HTTPException(status_code=403, detail="Fuck off")

    device_dict = {
        "nazov": device_data.name,
        "typ": device_data.type,
    }


    exit_code = Device.add_device(device_dict)


@router.get("/getDevices", response_model=GetDevicesResponse)
def get_devices(current_user=Depends(check_user)):
    if not isinstance(current_user, (Admin, Medic, Technic)):
        raise HTTPException(status_code=403, detail="Fuckey off")


    devices = Device.get_all_devices()

    device_responses = [
        Camera(
            id=device["id"],
            name=device["nazov"],
            type=device["typ"]
        )
        for device in devices
    ]

    return GetDevicesResponse(devices=device_responses)

@router.delete("/deleteDevice", status_code=204)
def delete_device(device_id: int, current_user=Depends(check_user)):
    if not isinstance(current_user, Admin):
        raise HTTPException(status_code=403, detail="Fuckey off")

    Device.delete_device_by_id(device_id)
    return {"message": "device_deleted_successfully"}

######

@router.post("/addDiagnosis", status_code=201)
def add_device(diagnose: Diagnoses, current_user=Depends(check_user)):
    if not isinstance(current_user, (Admin, Medic)):
        raise HTTPException(status_code=403, detail="Fuck off")

    exit_code = Diagnose.add_diagnose(diagnose.name)


@router.get("/getDiagnoses", response_model=GetDiagnoseResponse)
def get_devices(current_user=Depends(check_user)):
    if not isinstance(current_user, (Admin, Medic)):
        raise HTTPException(status_code=403, detail="Fuckey off")


    diagnoses = Diagnose.get_all_diagnoses()

    diagnose_response = [
        Diagnoses(
            id=diagnose["id_diagnozy"],
            name=diagnose["diagnoza"],
        )
        for diagnose in diagnoses
    ]

    return GetDiagnoseResponse(diagnoses=diagnose_response)


@router.delete("/deleteDiagnosis", status_code=204)
def delete_device(diagnose_id: int, current_user=Depends(check_user)):
    if not isinstance(current_user, Admin):
        raise HTTPException(status_code=403, detail="Fuckey off")

    Diagnose.delete_diagnose_by_id(diagnose_id)
    return {"message": "device_deleted_successfully"}

@router.get("/getMyInfo", response_model=UserOutPersonal)
def get_user_info(current_user=Depends(check_user)):
    if not isinstance(current_user, (Admin, Medic, Technic)):
        raise HTTPException(status_code=403, detail="Fuckey off")

    user = current_user._myself_model



    return UserOutPersonal(
        name=user.name,
        surname=user.surname,
        email=user.email,
        id=user.ID,
        sex=user.sex,
        date=user.date_of_birth  # <- teraz je to správny typ: str alebo None
    )


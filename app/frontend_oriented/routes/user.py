import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Request, Body
from fastapi.exceptions import RequestValidationError

from app.database_oriented.exitcodes_errors import InvalidTargetRoleError, ExitCodes
from app.database_oriented.others.additional_devices import AdditionalDevices
from app.database_oriented.others.devices import Device
from app.database_oriented.others.diagnoses import Diagnose
from app.database_oriented.others.methods import Method

from app.database_oriented.users.medic import Medic
from app.database_oriented.users.technic import Technic

from app.database_oriented.models.modelimages.model_original_image import ModelOriginalImage

from app.frontend_oriented.schemas.admin import GetPatientResponse
from app.frontend_oriented.schemas.image import QualityEnum, EyeEnum
from app.frontend_oriented.schemas.settings import DeviceCreate, GetDevices, DeviceOut, DeviceUpdate, DeviceDelete, \
    AdditionalDeviceCreate, GetAdditionalDevices, AdditionalDeviceOut, AdditionalDeviceUpdate, AdditionalDeviceDelete, \
    DiagnoseCreate, GetDiagnoses, DiagnoseOut, DiagnoseDelete, DiagnoseUpdate, MethodCreate, GetMethods, MethodOut, \
    MethodUpdate, MethodDelete

from app.frontend_oriented.schemas.user import CreatePatient, CreateTechnic, PatientOut, GetPatientResponse, \
    DeletePatient, GetUsersResponse, UserOut, UserOutPersonal
from app.frontend_oriented.services.auth import check_user, create_password, hash_password, check_rights

from app.frontend_oriented.services.token_service import TokenService
import app.database_oriented.keywords as kw


from app.database_oriented.users.admin import Admin

from app.frontend_oriented.services.email import EmailService
from app.frontend_oriented.utils.responses import ErrorErroor

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
from typing import Optional, Union




"""
    Routers for Device management
"""
@router.post("/addDevice", status_code=201)
def add_device(
    device_data: DeviceCreate,
    _: Union[Admin, Medic, Technic] = Depends(check_rights("add_device"))
):

    device_dict = {
        "nazov": device_data.name,
        "typ": device_data.type,
    }

    exit_code = Device.add_device(device_dict)

    if exit_code != ExitCodes.SUCCESS:
        raise ErrorErroor(error="failed_to_add_device")

@router.get("/getDevices", response_model=GetDevices)
def get_devices(_: Union[Admin, Medic, Technic] = Depends(check_rights("get_devices"))):

    devices = Device.get_all_devices()

    device_responses = [
        DeviceOut(
            id=device["id"],
            name=device["nazov"],
            type=device["typ"]
        )
        for device in devices
    ]

    return GetDevices(devices=device_responses)

@router.post("/editDevice", status_code=204)
def edit_device(
    device_data: DeviceUpdate,
    _: Union[Admin, Medic, Technic] = Depends(check_rights("edit_device"))
):

    device_dict = {
        "nazov": device_data.name,
        "typ": device_data.type
    }

    exit_code = Device.update_device_by_id(device_data.id, device_dict)

    if exit_code != ExitCodes.SUCCESS:
        raise ErrorErroor(error="failed_to_edit_device")

@router.delete("/deleteDevice", status_code=204)
def delete_device(
    device_data: DeviceDelete,
    _: Union[Admin, Medic, Technic] = Depends(check_rights("delete_device"))
):

    exit_code = Device.delete_device_by_id(device_data.id)

    if exit_code != ExitCodes.SUCCESS:
        raise ErrorErroor(error="failed_to_delete_device")


"""
    Routers for Additional device management
"""

@router.post("/addAdditionalDevice", status_code=201)
def add_additional_device(
    device_data: AdditionalDeviceCreate,
    _: Union[Admin, Medic, Technic] = Depends(check_rights("add_additional_device"))
):

    device_dict = {
        "nazov": device_data.name
    }

    exit_code = AdditionalDevices.add_additional_device(device_dict)

    if exit_code != ExitCodes.SUCCESS:
        raise ErrorErroor(error="failed_to_add_additional_device")

@router.get("/getAdditionalDevices", response_model=GetAdditionalDevices)
def get_additional_devices(_: Union[Admin, Medic, Technic] = Depends(check_rights("get_additional_devices"))):

    devices = AdditionalDevices.get_all_additional_devices()

    device_responses = [
        AdditionalDeviceOut(
            id=device["id_pz"],
            name=device["nazov"]
        )
        for device in devices
    ]

    return GetAdditionalDevices(devices=device_responses)

@router.post("/editAdditionalDevice", status_code=204)
def edit_additional_device(
    device_data: AdditionalDeviceUpdate,
    _: Union[Admin, Medic, Technic] = Depends(check_rights("edit_additional_device"))
):

    device_dict = {"nazov": device_data.name}

    exit_code = AdditionalDevices.update_additional_device_by_id(device_data.id, device_dict)

    if exit_code != ExitCodes.SUCCESS:
        raise ErrorErroor(error="failed_to_edit_additional_device")

@router.delete("/deleteAdditionalDevice", status_code=204)
def delete_additional_device(
    device_data: AdditionalDeviceDelete,
    _: Union[Admin, Medic, Technic] = Depends(check_rights("delete_additional_device"))
):

    exit_code = AdditionalDevices.delete_additional_device_by_id(device_data.id)

    if exit_code != ExitCodes.SUCCESS:
        raise ErrorErroor(error="failed_to_delete_additional_device")


"""
    Routers for Diagnosis management
"""

@router.post("/addDiagnosis", status_code=201)
def add_diagnosis(
    diagnose: DiagnoseCreate,
    _: Union[Admin, Medic, Technic] = Depends(check_rights("add_diagnosis"))
):

    exit_code = Diagnose.add_diagnose(diagnose.name)

    if exit_code != ExitCodes.SUCCESS:
        raise ErrorErroor(error="failed_to_add_diagnose")

@router.get("/getDiagnoses", response_model=GetDiagnoses)
def get_diagnosis(_: Union[Admin, Medic, Technic] = Depends(check_rights("get_diagnosis"))):

    diagnoses = Diagnose.get_all_diagnoses()

    diagnose_response = [
        DiagnoseOut(
            id=diagnose["id_diagnozy"],
            name=diagnose["diagnoza"],
        )
        for diagnose in diagnoses
    ]

    return GetDiagnoses(diagnoses=diagnose_response)

@router.post("/editDiagnosis", status_code=204)
def edit_diagnosis(
    diagnose: DiagnoseUpdate,
    _: Union[Admin, Medic, Technic] = Depends(check_rights("edit_diagnosis"))
):

    diagnose_dict = {"nazov": diagnose.name}

    #TODO: Not implemented in diagnoses.py


@router.delete("/deleteDiagnosis", status_code=204)
def delete_diagnosis(
    diagnose: DiagnoseDelete,
    _: Union[Admin, Medic, Technic] = Depends(check_rights("delete_diagnosis"))
):

    exit_code = Diagnose.delete_diagnose_by_id(diagnose.id)

    if exit_code != ExitCodes.SUCCESS:
        raise ErrorErroor(error="failed_to_delete_diagnose")

"""
    Routers for Methods management
"""

@router.post("/addMethod", status_code=201)
def add_method(
    method_data: MethodCreate,
    _: Union[Admin, Medic, Technic] = Depends(check_rights("add_method"))
):

    method_dict = {
        "nazov": method_data.name
    }

    exit_code = Method.add_method(method_dict)

    if exit_code != ExitCodes.SUCCESS:
        raise ErrorErroor(error="failed_to_add_method")

@router.get("/getMethods", response_model=GetMethods)
def get_method(_: Union[Admin, Medic, Technic] = Depends(check_rights("get_methods"))):

    methods = Method.get_all_methods()

    method_responses = [
        MethodOut(
            id=method["id"],
            name=method["metoda"]
        )
        for method in methods
    ]

    return GetMethods(methods=method_responses)

@router.post("/editMethod", status_code=204)
def edit_method(
    method_data: MethodUpdate,
    _: Union[Admin, Medic, Technic] = Depends(check_rights("edit_method"))
):

    method_dict = {"nazov": method_data.name}

    exit_code = Method.update_method_by_id(method_data.id, method_dict)

    if exit_code != ExitCodes.SUCCESS:
        raise ErrorErroor(error="failed_to_edit_method")

@router.delete("/deleteMethod", status_code=204)
def delete_method(
    method_data: MethodDelete,
    _: Union[Admin, Medic, Technic] = Depends(check_rights("delete_method"))
):

    exit_code = Method.delete_method_by_id(method_data.id)

    if exit_code != ExitCodes.SUCCESS:
        raise ErrorErroor(error="failed_to_delete_method")


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


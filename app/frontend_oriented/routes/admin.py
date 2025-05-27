





from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi import Response

from app.database_oriented.exitcodes_errors import InvalidTargetRoleError
from app.database_oriented.users import patient
from app.frontend_oriented.schemas.admin import TechnicOut, GetTechnicResponse, PatientOut, GetPatientResponse
from app.frontend_oriented.schemas.auth import GetAdminResponse, AdminOut, CreateUser, DeleteUser, DoctorOut, GetDoctorResponse
from app.frontend_oriented.services.token_service import TokenService
from app.frontend_oriented.services.auth import authenticate_user, check_user

from app.database_oriented.users.admin import Admin

from app.frontend_oriented.services.auth import create_password, hash_password


from app.frontend_oriented.services.email import EmailService



import app.database_oriented.keywords as kw


EmailService = EmailService()

router = APIRouter()
token_service = TokenService()

def check_rights(current_user):
    if not isinstance(current_user, Admin):
        raise HTTPException(status_code=403, detail= "Fuck off")

@router.get("/getAdmins", response_model= GetAdminResponse)
def get_admins(response: Response, current_user=Depends(check_user)):
    if not isinstance(current_user, Admin):
        raise HTTPException(status_code=403, detail= "Fuck off")

    admins = current_user.get_admins()


    user_responses = [
        AdminOut(
            name=admin["meno"],
            surname=admin["priezvisko"],
            email=admin["email"],
            id=admin["id"]
        )
        for admin in admins
    ]

    return GetAdminResponse(admins=user_responses)

@router.get("/getDoctors", response_model= GetDoctorResponse)
def get_doctors(response: Response, current_user=Depends(check_user)):
    if not isinstance(current_user, Admin):
        raise HTTPException(status_code=403, detail= "Fuck off")

    doctors = current_user.get_medics()

    user_responses = [
        DoctorOut(
            name=doctor["meno"],
            surname=doctor["priezvisko"],
            email=doctor["email"],
            id=doctor["id"]
        )
        for doctor in doctors
    ]

    print(user_responses)

    return GetDoctorResponse(doctors=user_responses)

@router.get("/getPatients", response_model= GetPatientResponse)
def get_patients(response: Response, current_user=Depends(check_user)):
    if not isinstance(current_user, Admin):
        raise HTTPException(status_code=403, detail= "Fuck off")
    patients = current_user.get_patients()

    user_responses = [
        PatientOut(
            name= "**",
            surname= "**",
            email= "aa@aa.com",                      #získať tieto údaje z databázy
            id= patient["pacient_id"],
            year_of_birth= patient["rok_narodenia"], #Vrátiť celý dátum
            sex= patient["pohlavie"]
    )
    for patient in patients
    ]

    return GetPatientResponse(patients=user_responses)


@router.get("/getTechnics", response_model=GetTechnicResponse)
def get_technics(response: Response, current_user=Depends(check_user)):
    if not isinstance(current_user, Admin):
        raise HTTPException(status_code=403, detail= "Fuck off")

    technics = current_user.get_technics()

    user_responses = [
        TechnicOut(
            name=technic["meno"],
            surname=technic["priezvisko"],
            email=technic["email"],
            id=technic["id"]
        )
        for technic in technics
    ]

    return GetTechnicResponse(technics=user_responses)

@router.post("/addDoctor")
def create_doctor(user_data: CreateUser, current_user=Depends(check_user)):
    if not isinstance(current_user, Admin):
        raise HTTPException(status_code=403, detail= "Fuck off")

    password = create_password(7)
    hashed_password = hash_password(password)

    user_dict = {
        "meno": user_data.name,
        "priezvisko": user_data.surname,
        "email": user_data.email
    }

    #EmailService.send_password_email(user_data.email, user_data.email, password)
    print(password)

    try:
        exit_code = current_user.add_user(kw.ROLE_MEDIC, user_dict, hashed_password)
        if exit_code != 0:
            raise HTTPException(status_code=400, detail=f"Failed to create user. Exit code: {exit_code}")
        doctor_model = current_user.selected_user
    except (PermissionError, InvalidTargetRoleError) as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    try:
        EmailService.send_password_email(str(user_data.email), user_data.name, password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create doctor: {str(e)}")

    return {"admin_id": doctor_model.ID}

@router.post("/addAdmin")
def create_admin(user_data: CreateUser, current_user=Depends(check_user)):
    if not isinstance(current_user, Admin):
        raise HTTPException(status_code=403, detail= "Fuck off")

    password = create_password(7)
    hashed_password = hash_password(password)
    user_dict = {
        "meno": user_data.name,
        "priezvisko": user_data.surname,
        "email": user_data.email
    }

    try:
        _, admin_model = current_user.add_admin(user_dict, hashed_password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create admin: {str(e)}")
    try:
        EmailService.send_password_email(str(user_data.email), user_data.name, password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create admin: {str(e)}")

    return {"admin_id": admin_model.ID}

@router.post("/addTechnic")
def create_technic(user_data: CreateUser, current_user=Depends(check_user)):
    if not isinstance(current_user, Admin):
        raise HTTPException(status_code=403, detail= "Fuck off")
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
        doctor_model = current_user.selected_user
    except (PermissionError, InvalidTargetRoleError) as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    #try:
        #EmailService.send_password_email(str(user_data.email), user_data.name, password)
    #except Exception as e:
        #raise HTTPException(status_code=500, detail=f"Failed to create doctor: {str(e)}")

@router.delete("/deleteUser")
def delete_doctor(user_data: DeleteUser = Body(...), current_user=Depends(check_user)):
    if not isinstance(current_user, Admin):
        raise HTTPException(status_code=403, detail= "Fuck off")

    current_user.delete_user_by_id(user_data.id)

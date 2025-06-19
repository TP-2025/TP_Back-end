from os import access

from fastapi import APIRouter, HTTPException, Depends
from fastapi import Response
from pydantic import EmailStr


from app.database_oriented.users.admin import Admin
from app.database_oriented.users.medic import Medic
from app.database_oriented.users.technic import Technic
from app.database_oriented.users.user import User

from app.frontend_oriented.schemas.auth import LoginRequest, LoginResponse, UserOut, ForgotPassword
from app.frontend_oriented.schemas.settings import ChangePassword, ChangePersonalInfo
from app.frontend_oriented.schemas.user import APIResponse
from app.frontend_oriented.services.auth import authenticate_user, check_user, hash_password, create_password
from app.frontend_oriented.services.token_service import TokenService
from app.frontend_oriented.services.email import EmailService
from app.frontend_oriented.utils.responses import ErrorErroor

router = APIRouter()
token_service = TokenService()
EmailService = EmailService()


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, response: Response):
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    data = {
        "user_id": user["id"],
        "role_id": user["role_id"],
        "email": user["email"]
    }

    jwt_token = token_service.create_access_token(data=data)

    response.set_cookie(
        key="access_token",
        value=jwt_token,
        httponly=True,  # Zabezpečí, že cookie nebude dostupná cez JS
        secure=True,  # Nastav na True v produkcii (HTTPS!)
        samesite="None",  # Alebo "Strict" / "None" (ak používaš cross-origin)
        max_age=7 * 24 * 60 * 60,  # 7 dní
        path="/"
    )

    user_response = {
        "id": str(user["id"]),  # konverzia na str ak model to vyžaduje
        "email": user["email"],
        "role_id": user["role_id"],
        "role": user["role"]
    }

    return LoginResponse(message= "Login succesful", user=UserOut(**user_response))


@router.post("/changePassword")
def change_password(request: ChangePassword, current_user=Depends(check_user)):
    if not isinstance(current_user, (Admin, Medic, Technic)):
        raise ErrorErroor(error="Forbidden")
    user = authenticate_user(request.email, request.old_password)
    if not user:
        raise ErrorErroor(error="old_password_is_invalid")

    hashed_password = hash_password(request.new_password)

    err = current_user.update_my_password(hashed_password)

    if err != 0:
        raise ErrorErroor(error="password_change_failed")


from datetime import datetime

@router.post("/changePersonalInfo", status_code=200)
def change_info(request: ChangePersonalInfo, current_user=Depends(check_user)):
    if not isinstance(current_user, (Admin, Medic, Technic)):
        raise ErrorErroor(error="Forbidden")



    birth_date_iso = None
    if request.birth_date:
        try:

            parsed_date = datetime.strptime(request.birth_date, "%d.%m.%Y")
            birth_date_iso = parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            raise ErrorErroor(error="invalid_date_format")


    change_info_dict = {
        "meno": request.name,
        "priezvisko": request.surname,
        "pohlavie": request.sex,
        "datum_narodenia": birth_date_iso
    }
    err = current_user.update_my_info(change_info_dict)

    if err != 0:
        raise ErrorErroor(error="personal_info_update_failed")

from fastapi import Form

@router.post("/forgotPassword")
def reset_password(user_data: ForgotPassword):
    password = create_password(7)
    hashed_password = hash_password(password)

    try:
        EmailService.send_password_email(user_data.email, "user_data.name", password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

    user = User.get_user_basic_info_by_email(user_data.email)


    role_id = user["role_id"]
    user_id = user["id"]

    match role_id:
        case 2: user = Technic(ID=user_id, token="token")
        case 3: user = Medic(ID=user_id, token="token")
        case 4: user = Admin(ID=user_id, token="token")
        case _: raise HTTPException(403, "Invalid role")

    err = user.update_my_password(hashed_password)
    if err != 0:
        raise HTTPException(status_code= 500, detail="server error")



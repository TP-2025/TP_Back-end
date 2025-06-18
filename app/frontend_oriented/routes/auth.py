from os import access

from fastapi import APIRouter, HTTPException, Depends
from fastapi import Response
from pydantic import EmailStr


from app.database_oriented.users.admin import Admin
from app.database_oriented.users.medic import Medic
from app.database_oriented.users.technic import Technic
from app.frontend_oriented.schemas.auth import LoginRequest, LoginResponse, UserOut
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


@router.post("/changePassword", response_model=APIResponse[None])
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

@router.post("/changePersonalInfo", response_model=APIResponse[None])
def change_info(request: ChangePersonalInfo, current_user=Depends(check_user)):
    if not isinstance(current_user, (Admin, Medic, Technic)):
        raise ErrorErroor(error="Forbidden")


    current_user.update_my_password(user_dict)

    class ChangePersonalInfo(BaseModel):
        name: Optional[str] = None
        surname: Optional[str] = None
        birth_date: Optional[date] = None
        sex: Optional[str] = None




@router.post("/forgotPassword")
def reset_password(user_data: EmailStr):
    password = create_password(7)
    hashed_password = hash_password(password)

    try:
        EmailService.send_password_email(str(user_data.email), user_data.name, password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")



    #err = current_user.update_my_password(hashed_password)
    #if err != 0:
    #    raise HTTPException(status_code= 500, detail="server error")



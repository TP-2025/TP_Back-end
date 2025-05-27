from os import access

from fastapi import APIRouter, HTTPException, Depends
from fastapi import Response

from app.frontend_oriented.schemas.auth import LoginRequest, LoginResponse, UserOut, ChangePassword
from app.frontend_oriented.services.auth import authenticate_user, check_user, hash_password
from app.frontend_oriented.services.token_service import TokenService

router = APIRouter()
token_service = TokenService()

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
    hashed_password = hash_password(request.password)
    err = current_user.update_my_password(hashed_password)
    if err != 0:
        raise HTTPException(status_code= 500, detail="server error")

#@router.post("/changeInformation")
#def change_information(current_user=Depends(check_user)):


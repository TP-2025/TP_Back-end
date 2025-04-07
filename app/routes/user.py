from fastapi import APIRouter, Depends, HTTPException
from app import schemas, models, database

router = APIRouter()


@router.get("/users/{id}", schemas.UserCheck)
def get_user(id: int):
    user = database.get_user()

@router.post("/login")
def login_user(request: schemas.UserLoginRequest):
    user = database.verify_user(request.email, request.password, request.role)
    if not user:
        raise HTTPException(status_code=401, detail="Wrong email or password")


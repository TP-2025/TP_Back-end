from fastapi import APIRouter, HTTPException
from app import schemas
from app.database_oriented import database

router = APIRouter()


@router.get("/users/{id}", schemas.UserCheck)
def get_user(id: int):
    user = database.get_user()

@router.post("/login")
def login_user(request: schemas.UserLoginRequest):



    user = database.verify_user(request.email, request.password, request.role)
    if not user:
        raise HTTPException(status_code=401, detail="Wrong email or password")


@router.post("/create_user")
def create_user(request: schemas.UserCreateRequest):


    #overenie povolení

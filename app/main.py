
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.frontend_oriented.routes import auth
from app.frontend_oriented.routes import admin
from app.frontend_oriented.routes import user
from app.frontend_oriented.routes import image
from app.frontend_oriented.utils.responses import ErrorErroor

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Nastav CORS, aby frontend (napr. React) mohol komunikovať s backendom
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # alebo ["*"] počas vývoja
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pripojenie route-ov
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

app.include_router(user.router, prefix="/api/user", tags=["user"])

app.include_router(image.router, prefix="/api/image", tags=["image"])

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(ErrorErroor)
async def error_erroor_handler(request: Request, exc: ErrorErroor):
    return JSONResponse(
        status_code=401 ,
        content={
            "success": False,
            "message": f"{exc.error}"},
    )

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import route modulov
from app.frontend_oriented.routes import auth  # napr. auth.py v routes priečinku
from app.frontend_oriented.routes import admin
from app.frontend_oriented.routes import user
from app.frontend_oriented.utils.responses import ErrorErroor

app = FastAPI()



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
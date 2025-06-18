
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import route modulov
from app.frontend_oriented.routes import auth  # napr. auth.py v routes priečinku
from app.frontend_oriented.routes import admin
from app.frontend_oriented.routes import user


from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging

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

#logger = logging.getLogger("uvicorn.error")

#@app.exception_handler(RequestValidationError)
#async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Zapíš chybu do logu
#    logger.error(f"Validation error: {exc.errors()}")
#    logger.error(f"Body: {await request.body()}")
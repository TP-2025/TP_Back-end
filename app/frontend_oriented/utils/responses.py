from fastapi.responses import JSONResponse
from typing import Optional, Any

class ErrorErroor(Exception):
    def __init__(self, error:str):
        self.error = error

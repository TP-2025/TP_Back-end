from app.database_oriented.database import Database
from app.database_oriented.models.modelusers.model_patient import ModelPatient
from app.database_oriented.models.modelusers.model_user import ModelUser
import app.database_oriented.keywords as kw


class ModelAdmin(ModelUser):
    def __init__(self, ID: int, name: str, surname: str, rights: int, role_id: int, **kwargs):
        super().__init__(ID, name, surname, rights, role_id, **kwargs)


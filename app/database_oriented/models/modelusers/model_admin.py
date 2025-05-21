from app.database_oriented.database import Database
from app.database_oriented.models.modelusers.model_patient import ModelPatient
from app.database_oriented.models.modelusers.model_user import ModelUser
import app.database_oriented.keywords as kw


class ModelAdmin(ModelUser):
    def __init__(self, ID: int, name: str, surname: str, rights: int, role_id: int):
        super().__init__(ID, name, surname, rights, role_id)

    @staticmethod
    def get_patients() -> list[ModelPatient]:
        db = Database()
        found_patients = db.select_patients("")  # TODO: maybe should be taken from user table
        db.close()

        # TODO: simplify the list
        simplified = []
        for patient in found_patients:
            try:
                simplified.append({
                    "id": patient[kw.KW_USER_ID],
                    "name": patient[kw.KW_USER_NAME],
                    "surname": patient[kw.KW_USER_SURNAME],
                })
            except KeyError:
                continue

        return simplified

    @staticmethod
    def get_technics() -> list[ModelUser]:
        db = Database()
        role = db.select_roles(f"{kw.KW_ROLE_NAME} = '{kw.ROLE_TECHNIC}'")[0]
        found_techs = db.select_users(f"{kw.KW_USER_ROLE_ID} = {role[kw.KW_ROLE_ID]}")
        db.close()

        # TODO: simplify the list
        simplified = []
        for tech in found_techs:
            try:
                simplified.append({
                    "id": tech[kw.KW_USER_ID],
                    "name": tech[kw.KW_USER_NAME],
                    "surname": tech[kw.KW_USER_SURNAME],
                })
            except KeyError:
                continue

        return simplified

    @staticmethod
    def get_medics() -> list[ModelUser]:
        db = Database()
        role = db.select_roles(f"{kw.KW_ROLE_NAME} = '{kw.ROLE_MEDIC}'")[0]
        found_medics = db.select_users(f"{kw.KW_USER_ROLE_ID} = {role[kw.KW_ROLE_ID]}")
        db.close()

        # TODO: simplify the list
        simplified = []
        for medic in found_medics:
            try:
                simplified.append({
                    "id": medic[kw.KW_USER_ID],
                    "name": medic[kw.KW_USER_NAME],
                    "surname": medic[kw.KW_USER_SURNAME],
                })
            except KeyError:
                continue

        return simplified

    @staticmethod
    def get_admins() -> list[ModelUser]:
        db = Database()
        role = db.select_roles(f"{kw.KW_ROLE_NAME} = '{kw.ROLE_ADMIN}'")[0]
        found_admins = db.select_users(f"{kw.KW_USER_ROLE_ID} = {role[kw.KW_ROLE_ID]}")
        db.close()

        # TODO: simplify the list
        simplified = []
        for admin in found_admins:
            try:
                simplified.append({
                    "id": admin[kw.KW_USER_ID],
                    "name": admin[kw.KW_USER_NAME],
                    "surname": admin[kw.KW_USER_SURNAME],
                })
            except KeyError:
                continue

        return simplified

    @staticmethod
    def get_original_images() -> list[dict]:
        db = Database()
        found_original_images = db.select_original_images("")
        db.close()
        # TODO: simplify the list
        simplified = []
        for image in found_original_images:
            try:
                simplified.append({
                    "id": image[kw.KW_USER_ID],
                    #"name": image[kw.KW_USER_NAME],
                    #"surname": image[kw.KW_USER_SURNAME],
                })
            except KeyError:
                continue
        return simplified

    @staticmethod
    def get_processed_images() -> list[dict]:
        db = Database()
        found_processed_images = db.select_processed_images("")
        db.close()
        # TODO: simplify the list
        simplified = []
        for image in found_processed_images:
            try:
                simplified.append({
                    "id": image[kw.KW_USER_ID],
                    #"name": image[kw.KW_USER_NAME],
                    #"surname": image[kw.KW_USER_SURNAME],
                })
            except KeyError:
                continue
        return simplified

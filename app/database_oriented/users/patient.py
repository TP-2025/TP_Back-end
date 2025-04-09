from typing import overload

from app.database_oriented.database import Database
from app.database_oriented.models.model_patient import ModelPatient
from app.database_oriented.models.model_user import ModelUser
from app.database_oriented.users.user import User


class Patient(User):
    def __init__(self, ID: int, full_name: str):
        super().__init__(ID, 0, User.ROLE_PATIENT, full_name)

    @staticmethod
    def get_patient(ID: int) -> "Patient":
        db = Database()
        found = db.select_users(f"{ModelUser.KW_ID} = {ID}")
        try:
            user = ModelUser.constructor(found[0])
            assert user.role == User.ROLE_PATIENT, f"User with given ID {ID} is not {User.ROLE_PATIENT}"
            db.close()
        except IndexError:
            db.close()
            raise IndexError(f"User with given ID '{ID}' not found")
        except AssertionError as e:
            db.close()
            raise AssertionError(e)

        return Patient(ID, user.full_name)

    def change_rights(self, rights: int, userID: int):
        raise PermissionError("Patients are not allowed to change rights")

    def update_rights(self, allow_rights: int, deny_rights: int, userID: int):
        raise PermissionError("Patients are not allowed to change rights")

    def is_change_of_rights_allowed(self, user: ModelUser, rights: int) -> bool:
        return False

    def is_allowed_to_add_users(self, role: str) -> bool:
        return False

    @staticmethod
    def add_user(email: str, full_name: str, hashed_password: str, role: str) -> int:
        raise PermissionError("Patients are not allowed to add users")

    def search_patients(self, condition: str, medicID: int, simplified: bool = True) -> list:
        raise PermissionError("Patients are not allowed to search patients")

    @staticmethod
    def get_user_info(email: str) -> [dict, None]:
        raise PermissionError("Patients are not allowed to get user info")

    def select_patient(self, patientID: int, safe_mode: bool = False) -> [ModelPatient, None]:
        return super().select_patient(self.ID, safe_mode)  # maybe should raise permissionError

    def add_patient_info(self, patient_userID: int, year_of_birth: int = -1, sex: str = "Unknown",
                         diagnosis: str = "Unknown", medical_notes: str = "", medic_id: int = -1) -> int:
        raise PermissionError("Patients are not allowed to add patient info of other patients")

    def update_my_patient_info(self, data: dict) -> int:
        db = Database()
        data_to_update = {
            key: value for key, value in data.items() if key in (
                ModelPatient.KW_NAME, ModelPatient.KW_SURNAME, ModelPatient.KW_MEDIC_ID, ModelPatient.KW_YEAR_OF_BIRTH,
                ModelPatient.KW_SEX, ModelPatient.KW_DIAGNOSIS, ModelPatient.KW_MEDICAL_NOTES)
        }
        exit_code = db.update_patients(data_to_update, f"{ModelPatient.KW_ID} = {self.ID}")
        db.close()
        return exit_code

    def delete_selected_patient(self, patient: ModelPatient):
        raise PermissionError("Patients are not allowed to delete patients")





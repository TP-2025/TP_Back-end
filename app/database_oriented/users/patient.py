from app.database_oriented.database import Database
from app.database_oriented.models.model_patient import ModelPatient
from app.database_oriented.models.model_user import ModelUser
from app.database_oriented.users.user import User


class Patient(User):
    def __init__(self, ID: int, full_name: str):
        super().__init__(ID, 0, User.ROLE_PATIENT, full_name)

    @staticmethod
    def get_patient(ID: int) -> "Patient":
        """
        Creates Patient object based on id
        :param ID: patient user id
        :return: (Patient)
        """
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

    def change_rights(self, rights: int, userID: int) -> int:
        """
        Function updates rights of user, for patient disabled.
        :param rights: (int) new rights of user
        :param userID: (int) ID of user
        :return: (int) Exit code
        :raise: PermissionError
        """
        raise PermissionError("Patients are not allowed to change rights")

    def update_rights(self, allow_rights: int, deny_rights: int, userID: int) -> int:
        """
        Function updates rights of user, for patient disabled.
        :param allow_rights: (int) rights to allow
        :param deny_rights: (int) rights to deny
        :param userID: (int) ID of user
        :return: (int) Exit code
        :raise: PermissionError
        """
        raise PermissionError("Patients are not allowed to change rights")

    def is_change_of_rights_allowed(self, user: ModelUser, rights: int) -> bool:
        """
        Function checks if user is allowed to change rights
        :param user: (app.models.user.User)
        :param rights:
        :return: (bool) False, patients are not allowed to change rights
        """
        return False

    def is_allowed_to_add_users(self, role: str) -> bool:
        """
        Function checks if user is allowed to add users of given role
        :param role: (str) role of user (lekar, technik, pacient)
        :return: (bool) False, patients are not allowed to add users
        """
        return False

    @staticmethod
    def add_user(email: str, full_name: str, hashed_password: str, role: str) -> int:
        """
        Function adds user to database, for patient disabled
        :param email: (str) email of user
        :param full_name: (str) full name of user in format "Priezvisko Meno"
        :param hashed_password: (str) hashed password of user
        :param role: (str) role of user
        :return: (int) Exit code
        :raise: PermissionError
        """
        raise PermissionError("Patients are not allowed to add users")

    def search_patients(self, condition: str, medicID: int, simplified: bool = True) -> list:
        """
        Function searches for patients in database, for patient disabled
        :param condition: (str) SQL WHERE condition
        :param medicID: (int) ID of medic to filter the patients.
        :param simplified: (bool) if True, returns simplified list
        :return: (list) list of patients
        :raise: PermissionError
        """
        raise PermissionError("Patients are not allowed to search patients")

    @staticmethod
    def get_user_info(email: str) -> [dict, None]:
        """
        Returns dictionary of user info, if user is present in database, patients cannot get user info
        :return: [dict, None] returns dictionary of user info or None if user not found
        :raise: PermissionError
        """
        raise PermissionError("Patients are not allowed to get user info")

    def select_one_patient(self, patientID: int, safe_mode: bool = False) -> [ModelPatient, None]:
        """
        Selects patient with a given ID from database
        :param patientID:
        :param safe_mode: (bool) if True, returns only non-sensitive data
        :return: [Patient, None] returns selected Patient object or None
        """
        return super().select_one_patient(self.ID, safe_mode)  # TO THINK: maybe should raise permissionError

    def add_patient_info(self, patient_userID: int, year_of_birth: int = -1, sex: str = "Unknown",
                         diagnosis: str = "Unknown", medical_notes: str = "", medic_id: int = -1) -> int:
        """
        Adds patient data to database, needs to be called immediately after adding patient user to database by add_user,
        for patient disabled
        :param patient_userID: (int) ID of patient user in database
        :param year_of_birth: (int, optional) year of birth of patient
        :param sex: (str, optional) sex of patient
        :param diagnosis: (str, optional) diagnosis of patient
        :param medical_notes: (str, optional) medical notes of patient
        :param medic_id: (int, optional) ID of medic user
        :return: (int) 0 on success, 1 if user is not allowed to add patients
        :raise: PermissionError
        """
        raise PermissionError("Patients are not allowed to add patient info of other patients")

    def update_my_patient_info(self, data: dict) -> int:
        """
        Function updates patient data in database, runnable only for oneself
        :param data: (dict) dictionary of data to update
        :return: (int) exit code
        """
        db = Database()
        data_to_update = {
            key: value for key, value in data.items() if key in (
                ModelPatient.KW_NAME, ModelPatient.KW_SURNAME, ModelPatient.KW_MEDIC_ID, ModelPatient.KW_YEAR_OF_BIRTH,
                ModelPatient.KW_SEX, ModelPatient.KW_DIAGNOSIS, ModelPatient.KW_MEDICAL_NOTES)
        }
        exit_code = db.update_patients(data_to_update, f"{ModelPatient.KW_ID} = {self.ID}")
        db.close()
        return exit_code

    def delete_selected_patient(self, patient: ModelPatient) -> int:
        """
        Deletes selected patient from database, including images, for patient disabled
        :param patient: (ModelPatient) patient to delete
        :return: (int) exit code
        :raise: PermissionError
        """
        raise PermissionError("Patients are not allowed to delete patients")





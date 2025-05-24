from time import sleep

from app.database_oriented.database import Database
from app.database_oriented.models.modelusers.model_patient import ModelPatient
from app.database_oriented.users.user import User
import app.database_oriented.keywords as kw


class Patient(User):
    def __init__(self, ID: int, token: str):
        db = Database()
        found = db.get_patients(ID)
        db.close()

        try:
            patient_found = found[0]
            model_patient = ModelPatient.constructor({**patient_found, "safe_mode": False})
        except IndexError:
            raise IndexError(f"Patient with given ID '{ID}' not found")

        assert model_patient.role_name == kw.ROLE_PATIENT, f"User with given ID {ID} is not {kw.ROLE_PATIENT}"

        super().__init__(ID, model_patient.rights, model_patient.role_name, token, model_patient)
        self.selected_user = model_patient

    @staticmethod
    def add_patient(user_data: dict, hashed_password: str) -> (int, ModelPatient):
        required_keys = (kw.KW_USER_NAME, kw.KW_USER_SURNAME, kw.KW_USER_EMAIL, kw.KW_PATIENT_MEDIC_ID)
        for key in required_keys:
            if key not in user_data.keys():
                raise KeyError(f"Key '{key}' is required for patient creation")

        user_data[kw.KW_USER_ROLE_ID] = Database.get_role_id_by_name(kw.ROLE_PATIENT)
        user_data[kw.KW_USER_RIGHTS] = 0
        user_data["safe_mode"] = False
        user_data[kw.KW_USER_ID] = kw.V_EMPTY_INT
        user_data[kw.KW_PATIENT_ID] = kw.V_EMPTY_INT
        patient_model = ModelPatient.constructor(user_data)
        all_data = patient_model.deconstructor()
        all_data[kw.KW_USER_HASHED_PASSWORD] = hashed_password

        db = Database()
        exit_code = db.insert_one_user(all_data)
        try:
            found = User.get_user_basic_info_by_email(patient_model.email)
            patient_model.ID = found["id"]
            all_data[kw.KW_PATIENT_USER_ID] = patient_model.ID
        except IndexError:
            db.close()
            raise IndexError(f"User with given email '{patient_model.email}' not found")
        exit_code |= db.insert_one_patient(all_data)
        found = db.select_patients(f"{kw.KW_PATIENT_USER_ID} = {patient_model.ID}")
        try_again = 3
        while try_again > 0:
            try:
                patient_model.patient_id = found[0][kw.KW_PATIENT_ID]
                db.close()
                break
            except IndexError:
                sleep(0.5)
                try_again -= 1
                if try_again == 0:
                    db.close()
                    raise IndexError(f"Patient with given ID '{patient_model.ID}' not found")

        return exit_code, patient_model

    def change_user_rights(self, rights: int, userID: int) -> int:
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

    def is_change_of_rights_allowed(self, rights: int) -> bool:
        """
        Function checks if user is allowed to change rights
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

    def add_user(self, role: str, user_data: dict, hashed_password: str) -> int:
        """
        Function adds user to database, for patient disabled
        :param hashed_password:
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
    def get_user_basic_info_by_email(email: str) -> [dict, None]:
        """
        Returns dictionary of user info, if user is present in database, patients cannot get user info
        :return: [dict, None] returns dictionary of user info or None if user not found
        :raise: PermissionError
        """
        raise PermissionError("Patients are not allowed to get user info")

    # def select_one_patient(self, patientID: int, safe_mode: bool = False) -> [ModelPatient, None]:
    #     """
    #     Selects patient with a given ID from database
    #     :param patientID:
    #     :param safe_mode: (bool) if True, returns only non-sensitive data
    #     :return: [Patient, None] returns selected Patient object or None
    #     """
    #     return super().select_one_patient(self.ID, safe_mode)  # TO THINK: maybe should raise permissionError

    # def add_patient_info(self, patient_userID: int, year_of_birth: int = -1, sex: str = "Unknown",
    #                      diagnosis: str = "Unknown", medical_notes: str = "", medic_id: int = -1) -> int:
    #     """
    #     Adds patient data to database, needs to be called immediately after adding patient user to database by add_user,
    #     for patient disabled
    #     :param patient_userID: (int) ID of patient user in database
    #     :param year_of_birth: (int, optional) year of birth of patient
    #     :param sex: (str, optional) sex of patient
    #     :param diagnosis: (str, optional) diagnosis of patient
    #     :param medical_notes: (str, optional) medical notes of patient
    #     :param medic_id: (int, optional) ID of medic user
    #     :return: (int) 0 on success, 1 if user is not allowed to add patients
    #     :raise: PermissionError
    #     """
    #     raise PermissionError("Patients are not allowed to add patient info of other patients")

    def update_my_info(self, data: dict) -> int:
        """
        Function updates patient data in database, runnable only for oneself
        :param data: (dict) dictionary of data to update
        :return: (int) exit code
        """
        for key in data.keys():
            if key in (kw.KW_USER_HASHED_PASSWORD,):
                data.pop(key)

        db = Database()
        exit_code = db.update_patients(data, f"{kw.KW_PATIENT_USER_ID} = {self.ID}")
        exit_code |= db.update_users(data, f"{kw.KW_USER_ID} = {self.ID}")
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

    def select_patient_by_patient_id(self, patient_id):
        raise PermissionError("Not allowed to change selected user (self)")

    def select_user_by_id(self, userID: int) -> int:
        raise PermissionError("Not allowed to change selected user (self)")

    @staticmethod
    def send_bulk_original_images_for_processing(image_ids: list, additional_data: dict) -> int:
        raise PermissionError("Patients are not allowed to send bulk original images for processing")

    @staticmethod
    def send_original_image_for_processing(image_id: int, additional_data: dict, wrapped: Database = None) -> int:
        raise PermissionError("Patients are not allowed to send original image for processing")

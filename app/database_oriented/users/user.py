from app.database_oriented.database import Database
from app.database_oriented.exitcodes_errors import ExitCodes, InvalidTargetRoleError, UserNotFoundError
from app.database_oriented.models.modelusers.model_patient import ModelPatient
from app.database_oriented.models.modelusers.model_user import ModelUser
import app.database_oriented.keywords as kw
import app.database_oriented.users as users


class User:
    def __init__(self, ID: int, rights: int, role_name: str, token: str = None, model: ModelUser = None):
        self.ID = ID
        self.rights = rights
        self.role = role_name

        self._myself_model = model

        self.token = token
        self.selected_user = None
        self.selected_image = None

    @staticmethod
    def get_user_basic_info_by_email(email: str) -> [dict, None]:
        """
        Returns dictionary of user info, if user is present in database
        :return: [dict, None] returns dictionary of user info or None if user not found
        """
        db = Database()
        try:
            user = db.select_users(f"{kw.KW_USER_EMAIL} = '{email}'")[0]
        except IndexError:
            user = None
        db.close()

        if user:
            role = db.get_role_by_id(user[kw.KW_USER_ROLE_ID])
            return {
                "id": user[kw.KW_USER_ID],
                "email": user[kw.KW_USER_EMAIL],
                "role_id": user[kw.KW_USER_ROLE_ID],
                "role": role,
                "hashed_password": user[kw.KW_USER_HASHED_PASSWORD],
            }
        else:
            return None

    def is_allowed_to_add_users(self, target_role: str) -> bool:
        """
        Checks if user is allowed to add users of given role
        :param target_role: (str) role of user (lekar, technik, pacient)
        :return: (bool) True if user is allowed to add users of given role
        """
        if target_role == kw.ROLE_MEDIC:
            return bool(self.rights & kw.ALLOWED_TO_ADD_MEDICS)
        elif target_role == kw.ROLE_TECHNIC:
            return bool(self.rights & kw.ALLOWED_TO_ADD_TECHNICS)
        elif target_role == kw.ROLE_PATIENT:
            return bool(self.rights & kw.ALLOWED_TO_ADD_PATIENTS)
        else:
            return False

    def add_user(self, role: str, user_data: dict, hashed_password: str) -> int:
        """
        Adds user to database (needs to check the permission with user_object.is_allowed_to_add_users())
        :parameter
         - role: (str) role of user
         - user_data: (dict) dictionary of user data
         - hashed_password: (str) hashed password of user
        :return: (int) ExitCodes
        """
        if not self.is_allowed_to_add_users(role):
            raise PermissionError(f"Not allowed to add users with role {role}")

        if role == kw.ROLE_MEDIC:
            from app.database_oriented.users.medic import Medic
            exit_code, self.selected_user = Medic.add_medic(user_data, hashed_password)
        elif role == kw.ROLE_TECHNIC:
            from app.database_oriented.users.technic import Technic
            exit_code, self.selected_user = Technic.add_technic(user_data, hashed_password)
        elif role == kw.ROLE_PATIENT:
            from app.database_oriented.users.patient import Patient
            exit_code, self.selected_user = Patient.add_patient(user_data, hashed_password)
        elif role == kw.ROLE_ADMIN:
            from app.database_oriented.users.admin import Admin
            exit_code, self.selected_user = Admin.add_admin(user_data, hashed_password)
        else:
            raise InvalidTargetRoleError("Invalid role")

        return exit_code

    def get_rights(self) -> dict:
        """
        Returns dictionary of user rights
        :return: (dict) dictionary of user rights
        """
        return {
            "add_patients": bool(self.rights & kw.ALLOWED_TO_ADD_PATIENTS),
            "add_medics": bool(self.rights & kw.ALLOWED_TO_ADD_MEDICS),
            "add_technics": bool(self.rights & kw.ALLOWED_TO_ADD_TECHNICS),
            "see_all_patients": bool(self.rights & kw.ALLOWED_TO_SEE_ALL_PATIENTS),
            "see_all_technics": bool(self.rights & kw.ALLOWED_TO_SEE_ALL_TECHNICS),
            "see_all_medics": bool(self.rights & kw.ALLOWED_TO_SEE_ALL_MEDICS),
            "see_all_admins": bool(self.rights & kw.ALLOWED_TO_SEE_ALL_ADMINS),
            "delete_patients": bool(self.rights & kw.ALLOWED_TO_DELETE_PATIENTS),
            "delete_medics": bool(self.rights & kw.ALLOWED_TO_DELETE_MEDICS),
            "delete_technics": bool(self.rights & kw.ALLOWED_TO_DELETE_TECHNICS),
            "delete_admins": bool(self.rights & kw.ALLOWED_TO_DELETE_ADMINS),
            "see_medicals": bool(self.rights & kw.ALLOWED_TO_SEE_MEDICALS),
            "change_rights_for_medics": bool(self.rights & kw.ALLOWED_TO_CHANGE_RIGHTS_FOR_MEDICS),
            "change_rights_for_technics": bool(self.rights & kw.ALLOWED_TO_CHANGE_RIGHTS_FOR_TECHNICS),
            "change_roles": bool(self.rights & kw.ALLOWED_TO_CHANGE_ROLES),
            "add_images": bool(self.rights & kw.ALLOWED_TO_ADD_IMAGES),

        }

    def is_change_of_rights_allowed(self, rights: int) -> bool:
        """
        Function checks if user is allowed to change rights
        :parameter
         - user: (app.models.user.User)
         - rights: (int) use flags kw.ALLOWED_TO_...
        :return: (bool) is user allowed to change rights for the target user?
        """
        if self.selected_user is None:
            raise UserNotFoundError("No user selected")

        changed_bits = rights ^ self.selected_user.rights
        if self.selected_user.role_name == kw.ROLE_MEDIC:
            needed_bits = changed_bits | kw.ALLOWED_TO_CHANGE_RIGHTS_FOR_MEDICS
        elif self.selected_user.role_name == kw.ROLE_TECHNIC:
            needed_bits = changed_bits | kw.ALLOWED_TO_CHANGE_RIGHTS_FOR_TECHNICS
        else:
            return False
        return (needed_bits & self.rights) == needed_bits

    def select_user_by_id(self, userID: int) -> int:
        """
        Selects user with a given ID from database
        :parameter
         - userID: (int, optional) ID of user
         - email: (str, optional) email of user
        :return: (int) ExitCode
        """
        self.selected_user = ModelUser.get_user_by_id(userID)
        if self.selected_user is not None:
            return ExitCodes.SUCCESS
        else:
            return ExitCodes.USER_NOT_FOUND

    def select_patient_by_patient_id(self, patient_id):
        self.selected_user = ModelPatient.get_patient_by_patient_id(patient_id)
        if self.selected_user is not None:
            return ExitCodes.SUCCESS
        else:
            return ExitCodes.USER_NOT_FOUND

    def delete_selected_user(self) -> int:
        """
        Deletes selected user from database
        :return: (int) ExitCode
        """
        if self.selected_user is None:
            raise UserNotFoundError("No user selected")
        elif (((self.rights & kw.ALLOWED_TO_DELETE_PATIENTS and self.selected_user.role_name == kw.ROLE_PATIENT) or
              (self.rights & kw.ALLOWED_TO_DELETE_MEDICS and self.selected_user.role_name == kw.ROLE_MEDIC)) or
              (self.rights & kw.ALLOWED_TO_DELETE_TECHNICS and self.selected_user.role_name == kw.ROLE_TECHNIC)):
            exit_code = self.selected_user.delete_me()
            self.selected_user = None
            return exit_code
        else:
            raise PermissionError(f"Not allowed to delete users with role {self.selected_user.role}")

        # db = Database()
        # exit_code = db.delete_users(condition)
        # db.close()
        # self.selected_user = None
        # return exit_code

    def delete_user_by_id(self, userID: int) -> int:
        """
        Deletes user with a given ID from database
        :parameter
         - userID: (int) ID of user
        :return: (int) ExitCode
        """
        exit_code = self.select_user_by_id(userID)
        exit_code |= self.delete_selected_user()

        return exit_code

    def delete_patient_by_patient_id(self, patient_ID: int) -> int:
        """
        Deletes user with a given ID from database
        :parameter
         - userID: (int) ID of user
        :return: (int) ExitCode
        """
        exit_code = self.select_patient_by_patient_id(patient_ID)
        exit_code |= self.delete_selected_user()

        return exit_code

    def update_user_rights(self, allow_rights: int, deny_rights: int, userID: int) -> int:
        """
        Function updates rights of user
        :parameter
         - allow_rights: (int) rights to allow, use flags kw.ALLOWED_TO_...
         - deny_rights: (int) rights to deny, use flags kw.ALLOWED_TO_...
         - userID: (int) ID of user
        :return: (int) Exit code
        """
        db = Database()
        try:
            user = db.select_users(f"{kw.KW_USER_ID} = {userID}")[0]
        except IndexError:
            raise UserNotFoundError("User not found")

        user = ModelUser.constructor(user)
        rights = (user.rights | allow_rights) & (~deny_rights)
        allowed = self.is_change_of_rights_allowed(rights)
        if allowed:
            user._update_rights(rights)
            exit_code = db.update_users({kw.KW_USER_RIGHTS: rights}, f"{kw.KW_USER_ID} = {userID}")
            db.close()
            return exit_code
        else:
            db.close()
            raise PermissionError("Not allowed to change rights")

    def change_user_rights(self, rights: int, userID: int) -> int:
        """
        Function updates rights of user
        :parameter
         - rights: (int) new rights of user
         - userID: (int) ID of user
        :return: (int) Exit code
        """
        db = Database()
        try:
            user = db.select_users(f"{kw.KW_USER_ID} = {userID}")[0]
        except IndexError:
            raise UserNotFoundError("User not found")

        user = ModelUser.constructor(user)
        allowed = self.is_change_of_rights_allowed(rights)

        if allowed:
            user._update_rights(rights)
            exit_code = db.update_users({kw.KW_USER_RIGHTS: rights}, f"{kw.KW_USER_ID} = {userID}")
            db.close()
            return exit_code
        else:
            db.close()
            raise PermissionError("Not allowed to change rights")

    # def update_my_user_info(self, data: dict) -> int:
    #     """
    #     Function updates user info in database (only fot oneself)
    #     :param data: (dict) data to update (email, full name)
    #     :return: exit code (0 if success)
    #     """
    #     data_to_update = {
    #         key: value for key, value in data.items() if key in [kw.KW_USER_EMAIL, kw.KW_USER_FULL_NAME]
    #     }
    #     db = Database()
    #     exit_code = db.update_users(data_to_update, f"{kw.KW_USER_ID} = {self.ID}")
    #     db.close()
    #     return exit_code
    #
    # def update_my_password(self, hashed_password: str) -> int:
    #     """
    #     Function updates password in database (only for oneself)
    #     :param hashed_password: (str) new hashed password
    #     :return: (int) 0 if success
    #     """
    #     db = Database()
    #     exit_code = db.update_users({kw.KW_USER_HASHED_PASSWORD: hashed_password}, f"{kw.KW_USER_ID} = {self.ID}")
    #     db.close()
    #     return exit_code

    # def search_patients(self, condition: str, medicID: int, simplified: bool = True) -> list:
    #     """
    #     Searches in database for patients using SQL WHERE condition
    #     :parameter
    #      - condition: (str) SQL WHERE condition
    #      - medicID: (int) ID of medic to filter the patients.
    #         If -1, no filtering (usable with ALLOWED_TO_SEE_ALL_PATIENTS)
    #      - simplified: (bool) if True, returns simplified list
    #     :return: (list) list of patients
    #     """
    #     db = Database()
    #     if not (self.rights & kw.ALLOWED_TO_SEE_ALL_PATIENTS):
    #         condition = f"{ModelPatient.KW_MEDIC_ID} = {medicID}" + ("" if condition == "" else " AND ") + condition
    #     found_patients = db.select_patients(condition)
    #     db.close()
    #     if simplified:
    #         simplified_list = []
    #         for patient in found_patients:
    #             try:
    #                 simplified_list.append({
    #                     "id": patient[ModelPatient.KW_USER_ID],
    #                     "name": patient[ModelPatient.KW_NAME],
    #                     "surname": patient[ModelPatient.KW_SURNAME],
    #                 })
    #             except KeyError:
    #                 continue
    #         return simplified_list
    #     else:
    #         return found_patients

    # def select_one_patient(self, patientID: int, safe_mode: bool = False) -> [ModelPatient, None]:
    #     """
    #     Selects patient with a given ID from database
    #     :parameter
    #      - patientID:
    #      - safe_mode: (bool) if True, returns only non-sensitive data
    #     :return: [Patient, None] returns selected Patient object or None
    #     """
    #     db = Database()
    #     condition = f"{ModelPatient.KW_USER_ID} = {patientID}"
    #     if not (self.rights & kw.ALLOWED_TO_SEE_ALL_PATIENTS):
    #         condition = f"{ModelPatient.KW_MEDIC_ID} = {self.ID} AND " + condition
    #
    #     found = db.select_patients(condition)
    #     db.close()
    #     try:
    #         self.selected_patient = ModelPatient.constructor(found[0], safe_mode)
    #         return self.selected_patient
    #     except IndexError:
    #         return None

    # def add_patient_info(self, patient_userID: int, year_of_birth: int = -1, sex: str = "Unknown",
    #                      diagnosis: str = "Unknown", medical_notes: str = "", medic_id: int = -1) -> int:
    #     """
    #     Adds patient data to database, needs to be called immediately after adding patient user to database by add_user
    #     :parameter
    #      - patient_userID: (int) ID of patient user
    #      - year_of_birth: (int, optional) year of birth of patient
    #      - sex: (str, optional) sex of patient
    #      - diagnosis: (str, optional) diagnosis of patient
    #      - medical_notes: (str, optional) medical notes of patient
    #      - medic_id: (int, optional) ID of medic user
    #     :return: (int) 0 on success, 1 if user is not allowed to add patients
    #     :raises
    #      - UserNotFoundError: if patient is not a user
    #      - PermissionError: if user is not allowed to add patients
    #     """
    #
    #     if self.rights & kw.ALLOWED_TO_ADD_PATIENTS:
    #         db = Database()
    #         try:
    #             user = db.select_users(f"{kw.KW_USER_ID} = {patient_userID}")[0]
    #         except IndexError:
    #             raise UserNotFoundError("Patient is not a user")
    #
    #         name = user[ModelPatient.KW_NAME]
    #         surname = user[ModelPatient.KW_SURNAME]
    #
    #         exit_code = db.insert_one_patient({
    #             ModelPatient.KW_USER_ID: patient_userID,
    #             ModelPatient.KW_NAME: name,
    #             ModelPatient.KW_SURNAME: surname,
    #             ModelPatient.KW_USER_YEAR_OF_BIRTH: year_of_birth,
    #             ModelPatient.KW_USER_SEX: sex,
    #             ModelPatient.KW_PATIENT_DIAGNOSIS: diagnosis,
    #             ModelPatient.KW_MEDICAL_NOTES: medical_notes,
    #             ModelPatient.KW_MEDIC_ID: medic_id
    #         })
    #         db.close()
    #         return exit_code
    #     else:
    #         raise PermissionError("Not allowed to add patients")

    # def add_patient(self, email: str, name: str, surname: str, year_of_birth: int = -1, sex: str = "Unknown",
    #                 diagnosis: str = "Unknown", medical_notes: str = "", medic_id: int = -1):
    #     """
    #     Adds patient to database and adds patient info
    #     :parameter
    #      - email: (str) email of patient
    #      - name: (str) name of patient
    #      - surname: (str) surname of patient
    #      - year_of_birth: (int, optional) year of birth of patient
    #      - sex: (str, optional) sex of patient
    #      - diagnosis: (str, optional) diagnosis of patient
    #      - medical_notes: (str, optional) medical notes of patient
    #      - medic_id: (int, optional) ID of medic user
    #     :return: (int) Exitcode
    #     :raises
    #      - UserNotFoundError: if patient is not a user
    #      - PermissionError: if user is not allowed to add patients
    #     """
    #     if self.is_allowed_to_add_users(kw.ROLE_PATIENT):
    #         generated_password = "AAAAAAAAAAAAAAAAA"  # TODO: Needs implementing generation of hashed password
    #         exitcode = self.add_user(email, f"{name} {surname}", generated_password, "AAAAAAAAAAAAAA")
    #         try:
    #             patient = self.search_users(f"{kw.KW_USER_EMAIL} = {email}", False, False)[0]
    #         except IndexError:
    #             return exitcode | ExitCodes.DATABASE_SELECT_ERROR
    #         self.add_patient_info(patient[kw.KW_USER_ID], year_of_birth, sex, diagnosis, medical_notes, medic_id)
    #     else:
    #         raise PermissionError("Not allowed to add patients")

    # def delete_selected_patient(self) -> int:
    #     """
    #     Deletes selected patient from database, including images
    #     :return: (int) 0 on success, 1 if user is not allowed to delete patients
    #     :raise PermissionError: if user is not allowed to delete patients
    #     """
    #     if self.rights & kw.ALLOWED_TO_DELETE_PATIENTS and self.selected_patient is not None:
    #         condition = f"{ModelPatient.KW_USER_ID} = {self.selected_patient.ID}"
    #         db = Database()
    #         exit_code = db.delete_patients(condition)
    #         exit_code |= db.delete_processed_images(condition)
    #         exit_code |= db.delete_original_images(condition)
    #         db.close()
    #         self.selected_patient = None
    #         return exit_code
    #     else:
    #         raise PermissionError("Not allowed to delete patients")

    # def search_users(self, condition: str, simplified: bool = True, filtered: bool = True) -> list:
    #     db = Database()
    #     found_users = db.select_users(condition)
    #     db.close()
    #
    #     if filtered:
    #         for user in found_users:
    #             if user[kw.KW_USER_ID] in self.associated_users:
    #                 continue
    #             elif user[kw.KW_USER_ROLE] == kw.ROLE_ADMIN and self.rights & kw.ALLOWED_TO_SEE_ALL_ADMINS:
    #                 found_users.remove(user)
    #             elif user[kw.KW_USER_ROLE] == kw.ROLE_MEDIC and self.rights & kw.ALLOWED_TO_SEE_ALL_MEDICS:
    #                 found_users.remove(user)
    #             elif user[
    #                 kw.KW_USER_ROLE] == kw.ROLE_TECHNIC and self.rights & kw.ALLOWED_TO_SEE_ALL_TECHNICS:
    #                 found_users.remove(user)
    #             elif user[
    #                 kw.KW_USER_ROLE] == kw.ROLE_PATIENT and self.rights & kw.ALLOWED_TO_SEE_ALL_PATIENTS:
    #                 found_users.remove(user)
    #
    #     if simplified:
    #         simplified_list = []
    #         for user in found_users:
    #             try:
    #                 simplified_list.append({
    #                     "id": user[kw.KW_USER_ID],
    #                     "fullname": user[kw.KW_USER_FULL_NAME],
    #                 })
    #             except KeyError:
    #                 continue
    #         return simplified_list
    #     else:
    #         return found_users

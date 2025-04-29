from app.database_oriented.database import Database
from app.database_oriented.exitcodes_errors import ExitCodes, InvalidTargetRoleError, UserNotFoundError
from app.database_oriented.models.model_patient import ModelPatient
from app.database_oriented.models.model_user import ModelUser


class User:
    # rights
    ALLOWED_TO_ADD_PATIENTS = 1 << 0
    ALLOWED_TO_ADD_MEDICS = 1 << 1
    ALLOWED_TO_ADD_TECHNICS = 1 << 2
    ALLOWED_TO_SEE_ALL_PATIENTS = 1 << 3
    ALLOWED_TO_SEE_ALL_TECHNICS = 1 << 4
    ALLOWED_TO_SEE_ALL_MEDICS = 1 << 5
    ALLOWED_TO_SEE_ALL_ADMINS = 1 << 6
    ALLOWED_TO_DELETE_PATIENTS = 1 << 7
    ALLOWED_TO_DELETE_MEDICS = 1 << 8
    ALLOWED_TO_DELETE_TECHNICS = 1 << 9
    ALLOWED_TO_DELETE_ADMINS = 1 << 10
    ALLOWED_TO_SEE_MEDICALS = 1 << 11
    ALLOWED_TO_CHANGE_RIGHTS_FOR_MEDICS = 1 << 12
    ALLOWED_TO_CHANGE_RIGHTS_FOR_TECHNICS = 1 << 13
    ALLOWED_TO_CHANGE_ROLES = 1 << 14
    ALLOWED_TO_ADD_IMAGES = 1 << 15

    ALLOWED_ALL = (1 << 16) - 1

    # roles
    ROLE_ADMIN = "Admin"
    ROLE_MEDIC = "Lekar"
    ROLE_TECHNIC = "Technik"
    ROLE_PATIENT = "Pacient"

    def __init__(self, ID: int, rights: int, role: str, full_name: str, associated_users=None):
        self.ID = ID
        self.rights = rights
        self.role = role
        self.full_name = full_name

        self.token = None
        self.selected_patient = None
        self.selected_user = None
        self.selected_original_image = None
        self.selected_processed_image = None

    @staticmethod
    def get_user_info(email: str) -> [dict, None]:
        """
        Returns dictionary of user info, if user is present in database
        :return: [dict, None] returns dictionary of user info or None if user not found
        """
        db = Database()
        try:
            user = db.select_users(f"{ModelUser.KW_EMAIL} = '{email}'")[0]
        except IndexError:
            user = None
        db.close()

        if user:
            return {
                "id": user[ModelUser.KW_ID],
                "email": user[ModelUser.KW_EMAIL],
                "role": user[ModelUser.KW_ROLE],
                "hashed_password": user[ModelUser.KW_HASHED_PASSWORD],
            }
        else:
            return None

    def is_allowed_to_add_users(self, target_role: str) -> bool:
        """
        Checks if user is allowed to add users of given role
        :param target_role: (str) role of user (lekar, technik, pacient)
        :return: (bool) True if user is allowed to add users of given role
        """
        if target_role == User.ROLE_MEDIC:
            return bool(self.rights & User.ALLOWED_TO_ADD_MEDICS)
        elif target_role == User.ROLE_TECHNIC:
            return bool(self.rights & User.ALLOWED_TO_ADD_TECHNICS)
        elif target_role == User.ROLE_PATIENT:
            return bool(self.rights & User.ALLOWED_TO_ADD_PATIENTS)
        else:
            return False

    @staticmethod
    def add_user(email: str, full_name: str, role: str) -> int:
        """
        Adds user to database (needs to check the permission with user_object.is_allowed_to_add_users())
        :parameter
         - full_name: (str) full name of user in format "Priezvisko Meno"
         - email: (str) email of user
         - hashed_password: (str) hashed password of user
         - role: (str) role of user
        :return: (int) ExitCodes
        """

        if role == User.ROLE_MEDIC:
            rights = User.ALLOWED_TO_ADD_TECHNICS | User.ALLOWED_TO_ADD_PATIENTS  # | User.ALLOWED_TO_DELETE_PATIENT
        elif role == User.ROLE_TECHNIC:
            rights = User.ALLOWED_TO_ADD_PATIENTS  # | User.ALLOWED_TO_DELETE_PATIENT
        elif role == User.ROLE_PATIENT:
            rights = 0
        elif role == User.ROLE_ADMIN:
            rights = User.ALLOWED_ALL
            # raise InvalidTargetRoleError("Admin cannot be added")
        else:
            raise InvalidTargetRoleError("Invalid role")

        generated_password = "AAAAAAAAAAAAAAAAAAAAAAAAAA"

        db = Database()
        exit_code = db.insert_one_user(
            {
                ModelUser.KW_EMAIL: email,
                ModelUser.KW_FULL_NAME: full_name,
                # ModelUser.KW_RIGHTS: rights,   # TODO: add rights
                ModelUser.KW_HASHED_PASSWORD: generated_password,  # TODO: add hashed password
                ModelUser.KW_ROLE: role,
            }
        )
        print(f"R: {rights} == ", end="")
        db.close()
        return exit_code

    def get_rights(self) -> dict:
        """
        Returns dictionary of user rights
        :return: (dict) dictionary of user rights
        """
        return {
            "add_patients": bool(self.rights & User.ALLOWED_TO_ADD_PATIENTS),
            "add_medics": bool(self.rights & User.ALLOWED_TO_ADD_MEDICS),
            "add_technics": bool(self.rights & User.ALLOWED_TO_ADD_TECHNICS),
            "see_all_patients": bool(self.rights & User.ALLOWED_TO_SEE_ALL_PATIENTS),
            "see_all_technics": bool(self.rights & User.ALLOWED_TO_SEE_ALL_TECHNICS),
            "see_all_medics": bool(self.rights & User.ALLOWED_TO_SEE_ALL_MEDICS),
            "delete_patients": bool(self.rights & User.ALLOWED_TO_DELETE_PATIENTS),
            "delete_medics": bool(self.rights & User.ALLOWED_TO_DELETE_MEDICS),
            "delete_technics": bool(self.rights & User.ALLOWED_TO_DELETE_TECHNICS),
            "see_medicals": bool(self.rights & User.ALLOWED_TO_SEE_MEDICALS),
            "change_rights_for_medics": bool(self.rights & User.ALLOWED_TO_CHANGE_RIGHTS_FOR_MEDICS),
            "change_rights_for_technics": bool(self.rights & User.ALLOWED_TO_CHANGE_RIGHTS_FOR_TECHNICS),
            "change_roles": bool(self.rights & User.ALLOWED_TO_CHANGE_ROLES)
        }

    def is_change_of_rights_allowed(self, user: ModelUser, rights: int) -> bool:
        """
        Function checks if user is allowed to change rights
        :parameter
         - user: (app.models.user.User)
         - rights: (int) use flags User.ALLOWED_TO_...
        :return: (bool) is user allowed to change rights for the target user?
        """
        changed_bits = rights ^ user.rights
        if user.role == User.ROLE_MEDIC:
            needed_bits = changed_bits | User.ALLOWED_TO_CHANGE_RIGHTS_FOR_MEDICS
        elif user.role == User.ROLE_TECHNIC:
            needed_bits = changed_bits | User.ALLOWED_TO_CHANGE_RIGHTS_FOR_TECHNICS
        else:
            return False
        return (needed_bits & self.rights) == needed_bits

    def update_rights(self, allow_rights: int, deny_rights: int, userID: int) -> int:
        """
        Function updates rights of user
        :parameter
         - allow_rights: (int) rights to allow, use flags User.ALLOWED_TO_...
         - deny_rights: (int) rights to deny, use flags User.ALLOWED_TO_...
         - userID: (int) ID of user
        :return: (int) Exit code
        """
        db = Database()
        try:
            user = db.select_users(f"{ModelUser.KW_ID} = {userID}")[0]
        except IndexError:
            raise UserNotFoundError("User not found")

        user = ModelUser.constructor(user)
        rights = (user.rights | allow_rights) & (~deny_rights)
        allowed = self.is_change_of_rights_allowed(user, rights)
        if allowed:
            user.update_rights(rights)
            exit_code = db.update_users({ModelUser.KW_RIGHTS: rights}, f"{ModelUser.KW_ID} = {userID}")
            db.close()
            return exit_code
        else:
            db.close()
            raise PermissionError("Not allowed to change rights")

    def change_rights(self, rights: int, userID: int) -> int:
        """
        Function updates rights of user
        :parameter
         - rights: (int) new rights of user
         - userID: (int) ID of user
        :return: (int) Exit code
        """
        db = Database()
        try:
            user = db.select_users(f"{ModelUser.KW_ID} = {userID}")[0]
        except IndexError:
            raise UserNotFoundError("User not found")

        user = ModelUser.constructor(user)
        allowed = self.is_change_of_rights_allowed(user, rights)

        if allowed:
            user.update_rights(rights)
            exit_code = db.update_users({ModelUser.KW_RIGHTS: rights}, f"{ModelUser.KW_ID} = {userID}")
            db.close()
            return exit_code
        else:
            db.close()
            raise PermissionError("Not allowed to change rights")

    def update_my_user_info(self, data: dict) -> int:
        """
        Function updates user info in database (only fot oneself)
        :param data: (dict) data to update (email, full name)
        :return: exit code (0 if success)
        """
        data_to_update = {
            key: value for key, value in data.items() if key in [ModelUser.KW_EMAIL, ModelUser.KW_FULL_NAME]
        }
        db = Database()
        exit_code = db.update_users(data_to_update, f"{ModelUser.KW_ID} = {self.ID}")
        db.close()
        return exit_code

    def update_my_password(self, hashed_password: str) -> int:
        """
        Function updates password in database (only for oneself)
        :param hashed_password: (str) new hashed password
        :return: (int) 0 if success
        """
        db = Database()
        exit_code = db.update_users({ModelUser.KW_HASHED_PASSWORD: hashed_password}, f"{ModelUser.KW_ID} = {self.ID}")
        db.close()
        return exit_code

    def search_patients(self, condition: str, medicID: int, simplified: bool = True) -> list:
        """
        Searches in database for patients using SQL WHERE condition
        :parameter
         - condition: (str) SQL WHERE condition
         - medicID: (int) ID of medic to filter the patients.
            If -1, no filtering (usable with ALLOWED_TO_SEE_ALL_PATIENTS)
         - simplified: (bool) if True, returns simplified list
        :return: (list) list of patients
        """
        db = Database()
        if not (self.rights & User.ALLOWED_TO_SEE_ALL_PATIENTS):
            condition = f"{ModelPatient.KW_MEDIC_ID} = {medicID}" + ("" if condition == "" else " AND ") + condition
        found_patients = db.select_patients(condition)
        db.close()
        if simplified:
            simplified_list = []
            for patient in found_patients:
                try:
                    simplified_list.append({
                        "id": patient[ModelPatient.KW_ID],
                        "name": patient[ModelPatient.KW_NAME],
                        "surname": patient[ModelPatient.KW_SURNAME],
                    })
                except KeyError:
                    continue
            return simplified_list
        else:
            return found_patients

    def select_one_patient(self, patientID: int, safe_mode: bool = False) -> [ModelPatient, None]:
        """
        Selects patient with a given ID from database
        :parameter
         - patientID:
         - safe_mode: (bool) if True, returns only non-sensitive data
        :return: [Patient, None] returns selected Patient object or None
        """
        db = Database()
        condition = f"{ModelPatient.KW_ID} = {patientID}"
        if not (self.rights & User.ALLOWED_TO_SEE_ALL_PATIENTS):
            condition = f"{ModelPatient.KW_MEDIC_ID} = {self.ID} AND " + condition

        found = db.select_patients(condition)
        db.close()
        try:
            self.selected_patient = ModelPatient.constructor(found[0], safe_mode)
            return self.selected_patient
        except IndexError:
            return None

    def add_patient_info(self, patient_userID: int, year_of_birth: int = -1, sex: str = "Unknown",
                         diagnosis: str = "Unknown", medical_notes: str = "", medic_id: int = -1) -> int:
        """
        Adds patient data to database, needs to be called immediately after adding patient user to database by add_user
        :parameter
         - patient_userID: (int) ID of patient user
         - year_of_birth: (int, optional) year of birth of patient
         - sex: (str, optional) sex of patient
         - diagnosis: (str, optional) diagnosis of patient
         - medical_notes: (str, optional) medical notes of patient
         - medic_id: (int, optional) ID of medic user
        :return: (int) 0 on success, 1 if user is not allowed to add patients
        :raises
         - UserNotFoundError: if patient is not a user
         - PermissionError: if user is not allowed to add patients
        """

        if self.rights & User.ALLOWED_TO_ADD_PATIENTS:
            db = Database()
            try:
                user = db.select_users(f"{ModelUser.KW_ID} = {patient_userID}")[0]
            except IndexError:
                raise UserNotFoundError("Patient is not a user")

            name = user[ModelPatient.KW_NAME]
            surname = user[ModelPatient.KW_SURNAME]

            exit_code = db.insert_one_patient({
                ModelPatient.KW_ID: patient_userID,
                ModelPatient.KW_NAME: name,
                ModelPatient.KW_SURNAME: surname,
                ModelPatient.KW_YEAR_OF_BIRTH: year_of_birth,
                ModelPatient.KW_SEX: sex,
                ModelPatient.KW_DIAGNOSIS: diagnosis,
                ModelPatient.KW_MEDICAL_NOTES: medical_notes,
                ModelPatient.KW_MEDIC_ID: medic_id
            })
            db.close()
            return exit_code
        else:
            raise PermissionError("Not allowed to add patients")

    def add_patient(self, email: str, name: str, surname: str, year_of_birth: int = -1, sex: str = "Unknown",
                    diagnosis: str = "Unknown", medical_notes: str = "", medic_id: int = -1):
        """
        Adds patient to database and adds patient info
        :parameter
         - email: (str) email of patient
         - name: (str) name of patient
         - surname: (str) surname of patient
         - year_of_birth: (int, optional) year of birth of patient
         - sex: (str, optional) sex of patient
         - diagnosis: (str, optional) diagnosis of patient
         - medical_notes: (str, optional) medical notes of patient
         - medic_id: (int, optional) ID of medic user
        :return: (int) Exitcode
        :raises
         - UserNotFoundError: if patient is not a user
         - PermissionError: if user is not allowed to add patients
        """
        if self.is_allowed_to_add_users(User.ROLE_PATIENT):
            generated_password = "AAAAAAAAAAAAAAAAA"  # TODO: Needs implementing generation of hashed password
            exitcode = self.add_user(email, f"{name} {surname}", generated_password, User.ROLE_PATIENT)
            try:
                patient = self.search_users(f"{ModelUser.KW_EMAIL} = {email}", False, False)[0]
            except IndexError:
                return exitcode | ExitCodes.DATABASE_SELECT_ERROR
            self.add_patient_info(patient[ModelUser.KW_ID], year_of_birth, sex, diagnosis, medical_notes, medic_id)
        else:
            raise PermissionError("Not allowed to add patients")

    def delete_selected_patient(self) -> int:
        """
        Deletes selected patient from database, including images
        :return: (int) 0 on success, 1 if user is not allowed to delete patients
        :raise PermissionError: if user is not allowed to delete patients
        """
        if self.rights & User.ALLOWED_TO_DELETE_PATIENTS and self.selected_patient is not None:
            condition = f"{ModelPatient.KW_ID} = {self.selected_patient.ID}"
            db = Database()
            exit_code = db.delete_patients(condition)
            exit_code |= db.delete_processed_images(condition)
            exit_code |= db.delete_original_images(condition)
            db.close()
            self.selected_patient = None
            return exit_code
        else:
            raise PermissionError("Not allowed to delete patients")

    def search_users(self, condition: str, simplified: bool = True, filtered: bool = True) -> list:
        db = Database()
        found_users = db.select_users(condition)
        db.close()

        if filtered:
            for user in found_users:
                if user[ModelUser.KW_ID] in self.associated_users:
                    continue
                elif user[ModelUser.KW_ROLE] == User.ROLE_ADMIN and self.rights & User.ALLOWED_TO_SEE_ALL_ADMINS:
                    found_users.remove(user)
                elif user[ModelUser.KW_ROLE] == User.ROLE_MEDIC and self.rights & User.ALLOWED_TO_SEE_ALL_MEDICS:
                    found_users.remove(user)
                elif user[
                    ModelUser.KW_ROLE] == User.ROLE_TECHNIC and self.rights & User.ALLOWED_TO_SEE_ALL_TECHNICS:
                    found_users.remove(user)
                elif user[
                    ModelUser.KW_ROLE] == User.ROLE_PATIENT and self.rights & User.ALLOWED_TO_SEE_ALL_PATIENTS:
                    found_users.remove(user)

        if simplified:
            simplified_list = []
            for user in found_users:
                try:
                    simplified_list.append({
                        "id": user[ModelUser.KW_ID],
                        "fullname": user[ModelUser.KW_FULL_NAME],
                    })
                except KeyError:
                    continue
            return simplified_list
        else:
            return found_users

    def select_one_user(self, userID: int = -1, email: str = "") -> int:
        """
        Selects user with a given ID from database
        :parameter
         - userID: (int, optional) ID of user
         - email: (str, optional) email of user
        :return: (int) ExitCode
        """
        db = Database()
        if userID != -1:
            found = db.select_users(f"{ModelUser.KW_ID} = {userID}")
        else:
            found = db.select_users(f"{ModelUser.KW_EMAIL} = '{email}'")
        db.close()
        try:
            self.selected_user = ModelUser.constructor(found[0])
            return ExitCodes.SUCCESS
        except IndexError:
            return ExitCodes.USER_NOT_FOUND

    def delete_selected_user(self) -> int:
        """
        Deletes selected user from database
        :return: (int) ExitCode
        """
        if self.selected_user is None:
            raise UserNotFoundError("No user selected")
        elif self.rights & User.ALLOWED_TO_DELETE_PATIENTS and self.selected_user.role == User.ROLE_PATIENT:
            condition = f"{ModelUser.KW_ID} = {self.selected_user.ID}"
        elif self.rights & User.ALLOWED_TO_DELETE_MEDICS and self.selected_user.role == User.ROLE_MEDIC:
            condition = f"{ModelUser.KW_ID} = {self.selected_user.ID}"
        elif self.rights & User.ALLOWED_TO_DELETE_TECHNICS and self.selected_user.role == User.ROLE_TECHNIC:
            condition = f"{ModelUser.KW_ID} = {self.selected_user.ID}"
        else:
            raise PermissionError(f"Not allowed to delete users with role {self.selected_user.role}")
        db = Database()
        exit_code = db.delete_users(condition)
        db.close()
        self.selected_user = None
        return exit_code

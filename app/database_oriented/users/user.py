import app.database_oriented.keywords as kw
from app.database_oriented.database import Database
from app.database_oriented.exitcodes_errors import ExitCodes, InvalidTargetRoleError, UserNotFoundError
from app.database_oriented.models.modelimages.model_processed_image import ModelProcessedImage
from app.database_oriented.models.modelusers.model_patient import ModelPatient
from app.database_oriented.models.modelusers.model_user import ModelUser


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
        :raise: PermissionError - if user is not allowed to add users
        :raise: InvalidTargetRoleError - if target role is invalid
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

    @staticmethod
    def send_original_image_for_processing(image_id: int, additional_data: dict, wrapped: Database) -> (
    int, ModelProcessedImage):
        """
        Function sends original image for processing
        :param image_id: (int) image ID to send for processing
        :param additional_data: (dict) additional data needed to create processed image
        :param wrapped: (Database, optional) database object to use more efficient approach
        :return: (int) exit code
        :raise: IndexError if original image not found
        """
        if wrapped is None:
            db = Database()
        else:
            db = wrapped

        try:
            oimage = db.select_original_images(f"{kw.KW_IMAGE_ID} = {image_id}")[0]
        except IndexError:
            raise IndexError(f"Original image with given ID '{image_id}' not found")

        all_data = {**additional_data, kw.KW_PIMAGE_ID: kw.V_EMPTY_INT,
                    kw.KW_PIMAGE_OIMAGE_ID: image_id, kw.KW_PIMAGE_EYE: oimage[kw.KW_IMAGE_EYE]}

        if wrapped is None:
            db.close()

        return ModelProcessedImage.add_processed_image(all_data)

    @staticmethod
    def send_bulk_original_images_for_processing(image_ids: list, additional_data: dict) -> int:
        """
        Function sends bulk original images for processing
        :param image_ids: (list) list of image IDs
        :param additional_data: (dict) additional data
        :return: (int) exit code
        :raise: PermissionError if user is not allowed to send bulk original images for processing
        """
        db = Database()
        success = ExitCodes.SUCCESS
        for image_id in image_ids:
            success |= User.send_original_image_for_processing(image_id, additional_data, db)[0]
        db.close()
        return success

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
        :raise: UserNotFoundError if no user selected
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

    def select_patient_by_patient_id(self, patient_id) -> int:
        """
        Selects patient with a given ID from database
        :param patient_id: (int) ID of patient to select
        :return: (int) ExitCode
        """
        self.selected_user = ModelPatient.get_patient_by_patient_id(patient_id)
        if self.selected_user is not None:
            return ExitCodes.SUCCESS
        else:
            return ExitCodes.USER_NOT_FOUND

    def delete_selected_user(self) -> int:
        """
        Deletes selected user from database
        :return: (int) ExitCode
        :raise: UserNotFoundError if no user selected
        :raise: PermissionError if user is not allowed to delete selected user
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
            #raise PermissionError(f"Not allowed to delete users with role {self.selected_user.role}")
            raise PermissionError(f"Not allowed to delete users with role")

    def delete_user_by_id(self, userID: int) -> int:
        """
        Deletes user with a given ID from database
        :parameter
         - userID: (int) ID of user
        :return: (int) ExitCode
        :raise: PermissionError if user is not allowed to delete selected user
        :raise: UserNotFoundError if no user selected or user not found
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
        :raise: PermissionError if user is not allowed to delete selected user
        :raise: UserNotFoundError if no user selected or user not found
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
        :raise: UserNotFoundError if no user selected
        :raise: PermissionError if user is not allowed to change rights
        """
        db = Database()
        try:
            user = db.select_users(f"{kw.KW_USER_ID} = {userID}")[0]
        except IndexError:
            db.close()
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
        :raise: UserNotFoundError if no user selected
        :raise: PermissionError if user is not allowed to change rights
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

    def update_my_info(self, data: dict) -> int:
        """
        Function updates user info in database (only fot oneself)
        :param data: (dict) data to update (email, name; surname; year of birth; sex) (not hashed password)
        :return: (int) exit code
        """
        for key in data.keys():
            if key in (kw.KW_USER_HASHED_PASSWORD,):
                data.pop(key)

        db = Database()
        exit_code = db.update_users(data, f"{kw.KW_USER_ID} = {self.ID}")
        db.close()
        return exit_code

    def update_my_password(self, hashed_password: str) -> int:
        """
        Function updates password in database (only for oneself)
        :param hashed_password: (str) new hashed password
        :return: (int) Exit code
        """
        db = Database()
        exit_code = db.update_users({kw.KW_USER_HASHED_PASSWORD: hashed_password}, f"{kw.KW_USER_ID} = {self.ID}")
        db.close()
        return exit_code

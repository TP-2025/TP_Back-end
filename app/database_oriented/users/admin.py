import app.database_oriented.keywords as kw
from app.database_oriented.database import Database
from app.database_oriented.models.modelusers.model_admin import ModelAdmin
from app.database_oriented.users.user import User


class Admin(User):
    def __init__(self, ID: int, token: str):
        db = Database()
        found = db.get_users(ID)
        db.close()

        try:
            model_admin = ModelAdmin.constructor(found[0])
        except IndexError:
            raise IndexError(f"User with given ID '{ID}' not found")

        assert model_admin.role_name == kw.ROLE_ADMIN, f"User with given ID {ID} is not {kw.ROLE_ADMIN}"
        super().__init__(ID, model_admin.rights, model_admin.role_name, token, model_admin)

    @staticmethod
    def add_admin(user_data: dict, hashed_password: str) -> (int, ModelAdmin):
        """
        Adds admin to database
        :param user_data: (dict) dictionary of user data
        :param hashed_password: (str) hashed password
        :return: (int, ModelAdmin) exit_code, admin model object of added admin
        :raise: KeyError if admin doesn't have name, surname, email
        :raise: IndexError if user was not successfully added to database
        """
        required_keys = (kw.KW_USER_NAME, kw.KW_USER_SURNAME, kw.KW_USER_EMAIL)
        for key in required_keys:
            if key not in user_data.keys():
                raise KeyError(f"Key '{key}' is required for admin creation")

        user_data[kw.KW_USER_ROLE_ID] = Database.get_role_id_by_name(kw.ROLE_ADMIN)
        user_data[kw.KW_USER_RIGHTS] = kw.ALLOWED_ALL
        user_data[kw.KW_USER_ID] = kw.V_EMPTY_INT
        admin_model = ModelAdmin.constructor(user_data)
        all_data = admin_model.deconstructor()
        all_data[kw.KW_USER_HASHED_PASSWORD] = hashed_password

        db = Database()
        exit_code = db.insert_one_user(all_data)
        try:
            found = User.get_user_basic_info_by_email(admin_model.email)
            admin_model.ID = found[kw.KW_USER_ID]
            db.close()
        except IndexError:
            db.close()
            raise IndexError(f"User with given email '{admin_model.email}' not found")

        return exit_code, admin_model

    @staticmethod
    def get_technics() -> list[dict]:
        """
        Returns list of technics
        :return: (list[dict]) list of technics
        """
        db = Database()
        role_id = Database.get_role_id_by_name(kw.ROLE_TECHNIC)
        found_technics = db.select_users(f"{kw.KW_USER_ROLE_ID} = {role_id}")
        db.close()
        simplified = []
        for medic in found_technics:
            try:
                simplified.append({
                    kw.KW_USER_ID: medic[kw.KW_USER_ID],
                    kw.KW_USER_SEX: medic[kw.KW_USER_SEX],
                    kw.KW_USER_DATE_OF_BIRTH: medic[kw.KW_USER_DATE_OF_BIRTH],
                })
            except KeyError:
                continue
        # TODO: make return simplified if needed
        return found_technics

    @staticmethod
    def get_patients() -> list[dict]:
        """
        Returns list of patients
        :return: (list[dict]) list of patients
        """
        db = Database()
        found_patients = db.get_patients()
        db.close()
        simplified = []
        for patient in found_patients:
            try:
                simplified.append({
                    kw.KW_PATIENT_ID: patient[kw.KW_PATIENT_ID],
                    kw.KW_USER_SEX: patient[kw.KW_USER_SEX],
                    kw.KW_USER_DATE_OF_BIRTH: patient[kw.KW_USER_DATE_OF_BIRTH],
                })
            except KeyError:
                continue
        #TODO: Zmeniť podľa potreby
        #return simplified
        return found_patients
    @staticmethod
    def get_medics() -> list[dict]:
        """
        Returns list of medics
        :return: (list[dict]) list of medics
        """
        db = Database()
        role_id = Database.get_role_id_by_name(kw.ROLE_MEDIC)
        found_medics = db.select_users(f"{kw.KW_USER_ROLE_ID} = {role_id}")
        db.close()
        simplified = []
        for medic in found_medics:
            try:
                simplified.append({
                    kw.KW_USER_ID: medic[kw.KW_USER_ID],
                    kw.KW_USER_SEX: medic[kw.KW_USER_SEX],
                    kw.KW_USER_DATE_OF_BIRTH: medic[kw.KW_USER_DATE_OF_BIRTH],
                })
            except KeyError:
                continue
        # TODO: make return simplified if needed
        return found_medics

    @staticmethod
    def get_admins() -> list[dict]:
        """
        Returns list of admins
        :return: (list[dict]) list of admins
        """
        db = Database()
        role_id = Database.get_role_id_by_name(kw.ROLE_ADMIN)
        found_admins = db.select_users(f"{kw.KW_USER_ROLE_ID} = {role_id}")
        db.close()
        simplified = []
        for admin in found_admins:
            try:
                simplified.append({
                    kw.KW_USER_ID: admin[kw.KW_USER_ID],
                    kw.KW_USER_SEX: admin[kw.KW_USER_SEX],
                    kw.KW_USER_DATE_OF_BIRTH: admin[kw.KW_USER_DATE_OF_BIRTH],
                })
            except KeyError:
                continue

        # TODO: make return simplified if needed
        return found_admins

    @staticmethod
    def get_original_images(sql_where: str = "") -> list[dict]:
        """
        Returns original images
        :param sql_where: (str) sql where condition
        :return: (list[dict]) list of original images
        """
        db = Database()
        found_original_images = db.select_original_images(sql_where)
        db.close()
        # TODO: make return simplified if needed
        return found_original_images

    @staticmethod
    def get_processed_images(sql_where: str = "") -> list[dict]:
        """
        Returns processed images
        :param sql_where: (str) sql where condition
        :return: (list[dict]) list of processed images
        """
        db = Database()
        found_processed_images = db.select_processed_images(sql_where)
        db.close()
        # TODO: make return simplified if needed
        return found_processed_images

    def is_allowed_to_add_users(self, target_role: str) -> bool:
        """
        Checks if user is allowed to add users of given role (admin can add any user)
        :param target_role: (str) role of user (lekar, technik, pacient)
        :return: (bool) True if user is allowed to add users of given role
        :return:
        """
        return True

    def is_change_of_rights_allowed(self, rights: int) -> bool:
        """
        Function checks if user is allowed to change rights
        :param rights:
        :return: (bool) True, admin can change rights
        """
        return True

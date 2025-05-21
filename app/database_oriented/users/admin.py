from app.database_oriented.database import Database
from app.database_oriented.models.modelusers.model_admin import ModelAdmin
from app.database_oriented.models.modelusers.model_user import ModelUser
from app.database_oriented.users.user import User
import app.database_oriented.keywords as kw


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
            admin_model.ID = found["id"]
            db.close()
        except IndexError:
            db.close()
            raise IndexError(f"User with given email '{admin_model.email}' not found")

        return exit_code, admin_model

    def is_allowed_to_add_users(self, target_role: str) -> bool:
        """
        Checks if user is allowed to add users of given role (admin can add any user)
        :param target_role: (str) role of user (lekar, technik, pacient)
        :return: (bool) True if user is allowed to add users of given role
        :return:
        """
        return True

    def is_change_of_rights_allowed(self, user: ModelUser, rights: int) -> bool:
        """
        Function checks if user is allowed to change rights
        :param user: (app.models.user.User)
        :param rights:
        :return: (bool) True, admin can change rights
        """
        return True

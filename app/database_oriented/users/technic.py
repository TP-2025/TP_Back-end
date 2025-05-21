from app.database_oriented.database import Database
from app.database_oriented.models.modelusers.model_technic import ModelTechnic
from app.database_oriented.users.user import User
import app.database_oriented.keywords as kw


class Technic(User):
    def __init__(self, ID: int, token: str):
        db = Database()
        found = db.get_users(ID)
        db.close()

        try:
            model_technic = ModelTechnic.constructor(found[0])
        except IndexError:
            raise IndexError(f"User with given ID '{ID}' not found")

        assert model_technic.role_name == kw.ROLE_TECHNIC, f"User with given ID {ID} is not {kw.ROLE_TECHNIC}"
        super().__init__(ID, model_technic.rights, model_technic.role_name, token, model_technic)

    @staticmethod
    def add_technic(user_data: dict, hashed_password: str):
        required_keys = (kw.KW_USER_NAME, kw.KW_USER_SURNAME, kw.KW_USER_EMAIL)
        for key in required_keys:
            if key not in user_data.keys():
                raise KeyError(f"Key '{key}' is required for technic creation")

        user_data[kw.KW_USER_ROLE_ID] = Database.get_role_id_by_name(kw.ROLE_ADMIN)
        user_data[kw.KW_USER_RIGHTS] = kw.ALLOWED_TO_ADD_PATIENTS  # | kw.ALLOWED_TO_DELETE_PATIENT
        user_data[kw.KW_USER_ID] = kw.V_EMPTY_INT
        technic_model = ModelTechnic.constructor(user_data)
        all_data = technic_model.deconstructor()
        all_data[kw.KW_USER_HASHED_PASSWORD] = hashed_password

        db = Database()
        exit_code = db.insert_one_user(all_data)
        try:
            found = User.get_user_basic_info_by_email(technic_model.email)
            technic_model.ID = found["id"]
            db.close()
        except IndexError:
            db.close()
            raise IndexError(f"User with given email '{technic_model.email}' not found")

        return exit_code, technic_model

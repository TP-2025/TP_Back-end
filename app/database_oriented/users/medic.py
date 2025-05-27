from app.database_oriented.database import Database
from app.database_oriented.models.modelusers.model_medic import ModelMedic
from app.database_oriented.models.modelusers.model_user import ModelUser
from app.database_oriented.users.user import User
import app.database_oriented.keywords as kw


class Medic(User):
    def __init__(self, ID: int, token: str):
        db = Database()
        found = db.get_users(ID)
        db.close()

        try:
            model_medic = ModelUser.constructor(found[0])
        except IndexError:
            raise IndexError(f"User with given ID '{ID}' not found")

        assert model_medic.role_name == kw.ROLE_MEDIC, f"User with given ID {ID} is {model_medic.role_name} not {kw.ROLE_MEDIC}"
        super().__init__(ID, model_medic.rights, model_medic.role_name, token, model_medic)

    @staticmethod
    def add_medic(user_data: dict, hashed_password: str) -> (int, ModelMedic):
        """
        Adds medic to database
        :param user_data: (dict) dictionary of user data
        :param hashed_password: (str) hashed password
        :return: (int, ModelMedic) exit_code, medic model object of added medic
        :raise: KeyError if medic doesn't have name, surname, email
        :raise: IndexError if user was not successfully added to database
        """
        required_keys = (kw.KW_USER_NAME, kw.KW_USER_SURNAME, kw.KW_USER_EMAIL)
        for key in required_keys:
            if key not in user_data.keys():
                raise KeyError(f"Key '{key}' is required for medic creation")

        user_data[kw.KW_USER_ROLE_ID] = Database.get_role_id_by_name(kw.ROLE_MEDIC)
        user_data[kw.KW_USER_RIGHTS] = kw.ALLOWED_TO_ADD_TECHNICS | kw.ALLOWED_TO_ADD_PATIENTS  # | kw.ALLOWED_TO_DELETE_PATIENT
        user_data[kw.KW_USER_ID] = kw.V_EMPTY_INT
        medic_model = ModelMedic.constructor(user_data)
        all_data = medic_model.deconstructor()
        all_data[kw.KW_USER_HASHED_PASSWORD] = hashed_password

        db = Database()
        exit_code = db.insert_one_user(all_data)
        try:
            found = User.get_user_basic_info_by_email(medic_model.email)
            medic_model.ID = found["id"]
            db.close()
        except IndexError:
            db.close()
            raise IndexError(f"User with given email '{medic_model.email}' not found")

        return exit_code, medic_model

    def get_technics(self):
        # TODO: Needs rework and implementation about storing relation between medic and technics
        return self._myself_model.get_technics()

    def get_patients(self) -> list[dict]:
        """
        Returns list of patients associated with this medic
        :return: (list[dict]) list of patients
        """
        return self._myself_model.get_patients()

    def get_original_images(self) -> list[dict]:
        """
        Returns list of original images associated with this medic
        :return: (list[dict]) list of original images
        """
        return self._myself_model.get_original_images()

    def get_processed_images(self):
        """
        Returns list of processed images associated with this medic
        :return: (list[dict]) list of processed images
        """
        return self._myself_model.get_processed_images()

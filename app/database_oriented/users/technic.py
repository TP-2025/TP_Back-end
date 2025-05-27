import app.database_oriented.keywords as kw
from app.database_oriented.database import Database
from app.database_oriented.models.modelusers.model_technic import ModelTechnic
from app.database_oriented.users.user import User


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
    def add_technic(user_data: dict, hashed_password: str) -> (int, ModelTechnic):
        """
        Adds technic to database
        :param user_data: (dict) dictionary of user data
        :param hashed_password: (str) hashed password
        :return: (int, ModelTechnic) exit_code, technic model object of added technic
        :raise: KeyError if technic doesn't have name, surname, email
        :raise: IndexError if user was not successfully added to database
        """
        required_keys = (kw.KW_USER_NAME, kw.KW_USER_SURNAME, kw.KW_USER_EMAIL)
        for key in required_keys:
            if key not in user_data.keys():
                raise KeyError(f"Key '{key}' is required for technic creation")

        user_data[kw.KW_USER_ROLE_ID] = Database.get_role_id_by_name(kw.ROLE_TECHNIC)
        user_data[kw.KW_USER_RIGHTS] = kw.ALLOWED_TO_ADD_PATIENTS  # | kw.ALLOWED_TO_DELETE_PATIENT
        user_data[kw.KW_USER_ID] = kw.V_EMPTY_INT
        technic_model = ModelTechnic.constructor(user_data)
        all_data = technic_model.deconstructor()
        all_data[kw.KW_USER_HASHED_PASSWORD] = hashed_password

        db = Database()
        exit_code = db.insert_one_user(all_data)
        try:
            found = User.get_user_basic_info_by_email(technic_model.email)
            technic_model.ID = found[kw.KW_USER_ID]
            db.close()
        except IndexError:
            db.close()
            raise IndexError(f"User with given email '{technic_model.email}' not found")

        return exit_code, technic_model

    def get_medics(self):
        # TODO: implement this
        return self._myself_model.get_medics()

    def get_original_images(self) -> list[dict]:
        """
        Returns list of original images associated with this technic
        :return: (list[dict]) list of original images
        """
        return self._myself_model.get_original_images()

    @staticmethod
    def send_bulk_original_images_for_processing(image_ids: list, additional_data: dict) -> int:
        """
        Function sends bulk original images for processing
        :param image_ids: (list) list of image IDs
        :param additional_data: (dict) additional data
        :return: (int) exit code
        :raise: PermissionError - technics are not allowed to send bulk original images for processing
        """
        raise PermissionError("Technics are not allowed to send bulk original images for processing")

    @staticmethod
    def send_original_image_for_processing(image_id: int, additional_data: dict, wrapped: Database = None) -> int:
        """
        Function sends original image for processing
        :param image_id: (int) image ID
        :param additional_data: (dict) additional data
        :param wrapped: (Database) database object
        :return: (int) exit code
        :raise: PermissionError - technics are not allowed to send original image for processing
        """
        raise PermissionError("Technics are not allowed to send original image for processing")

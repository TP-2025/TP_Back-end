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

#    def get_medics(self):
        # TODO: implement this
#        return self._myself_model.get_medics()

# TODO: Zmeniť podľa potreby
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
                    kw.KW_USER_YEAR_OF_BIRTH: medic[kw.KW_USER_YEAR_OF_BIRTH],
                })
            except KeyError:
                continue
        # TODO: make return simplified if needed
        return found_medics

# TODO: Treba zistiť ako má vidieť technik pacientov, kvôli pridávaniu fotiek
    @staticmethod
    def get_patients() -> list[dict]:
        """
        Returns list of patients
        :return: (list[dict]) list of patients
        """
        db = Database()
        found_patients = db.get_patients()
        db.close()

        return found_patients

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

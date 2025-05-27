import app.database_oriented.keywords as kw
from app.database_oriented.database import Database
from app.database_oriented.models.modelusers.model_user import ModelUser


class ModelTechnic(ModelUser):
    def __init__(self, ID: int, name: str, surname: str, rights: int, role_id: int, **kwargs):
        super().__init__(ID, name, surname, rights, role_id, **kwargs)

    def get_medics(self):
        # TODO: Needs rework and implementation about storing relation between medic and technics
        # Many to many relation
        return []

    def get_original_images(self) -> list[dict]:
        """
        Returns list of original images connected to this technic (only image ID, device ID and path to image for each)
        :return: (list[dict]) simplified list of original images
        """
        db = Database()
        found_original_images = db.select_original_images(f"{kw.KW_IMAGE_TECHNIC_ID} = {self.ID}")
        db.close()
        # TODO: simplify the list
        simplified = []
        for image in found_original_images:
            try:
                simplified.append({
                    kw.KW_IMAGE_ID: image[kw.KW_IMAGE_ID],
                    kw.KW_IMAGE_DEVICE_ID: image.get(kw.KW_IMAGE_DEVICE_ID, kw.V_EMPTY_INT),
                    kw.KW_IMAGE_PATH: image.get(kw.KW_IMAGE_PATH, kw.V_EMPTY_STRING),
                    # "name": image[kw.KW_USER_NAME],
                    # "surname": image[kw.KW_USER_SURNAME],
                })
            except KeyError:
                continue
        return simplified

from app.database_oriented.database import Database
from app.database_oriented.models.model_original_image import ModelOriginalImage
from app.database_oriented.models.model_processed_image import ModelProcessedImage
from app.third_party.image_processing_server import IPS


class ModelPatient:
    # Keywords for accessing patient data in database
    KW_ID = "id"
    KW_NAME = "meno"
    KW_SURNAME = "priezvisko"
    KW_MEDIC_ID = "lekar_id"
    KW_YEAR_OF_BIRTH = "rok_narodenia"
    KW_SEX = "pohlavie"
    KW_DIAGNOSIS = "diagnoza"
    KW_MEDICAL_NOTES = "poznamka_lekara"

    # Default values of empty data
    V_EMPTY_STRING = "Nothing here"
    V_EMPTY_INT = -1111
    V_EMPTY_DICT = {"empty": "empty"}

    def __init__(self, ID: int, name: str, surname: str, year_of_birth: int, sex: str,
                 diagnosis: str, medical_notes: str, medic_id: int, safe_mode: bool):
        self.ID = ID
        self.name = name
        self.surname = surname
        self.year_of_birth = year_of_birth
        self.sex = sex
        self.diagnosis = diagnosis
        self.medical_notes = medical_notes
        self.medic_id = medic_id
        self.safe_mode = safe_mode

    @staticmethod
    def constructor(data: dict, safe_mode: bool) -> "ModelPatient":
        """Function to construct ModelPatient object from raw data in dictionary

        :param data: (dict) patient data
        :param safe_mode: (bool) loads only non-sensitive information
        :return: new ModelPatient object
        """
        try:
            ID = data[ModelPatient.KW_ID]
            medic_id = data.get(ModelPatient.KW_MEDIC_ID, ModelPatient.V_EMPTY_INT)
        except KeyError:
            raise KeyError("ModelPatient doesn't have ID or medic id, it cannot be constructed")

        name = data.get(ModelPatient.KW_NAME, ModelPatient.V_EMPTY_STRING)
        surname = data.get(ModelPatient.KW_SURNAME, ModelPatient.V_EMPTY_STRING)
        year_of_birth = data.get(ModelPatient.KW_YEAR_OF_BIRTH, ModelPatient.V_EMPTY_INT)
        sex = data.get(ModelPatient.KW_SEX, ModelPatient.V_EMPTY_STRING)
        if safe_mode:
            diagnosis = ModelPatient.V_EMPTY_STRING
            medical_notes = ModelPatient.V_EMPTY_STRING
        else:
            diagnosis = data.get(ModelPatient.KW_DIAGNOSIS, ModelPatient.V_EMPTY_STRING)
            medical_notes = data.get(ModelPatient.KW_MEDICAL_NOTES, ModelPatient.V_EMPTY_STRING)
        return ModelPatient(ID, name, surname, year_of_birth, sex, diagnosis, medical_notes, medic_id, safe_mode)

    def deconstructor(self) -> dict:
        """
        Function for deconstructing ModelPatient object into dict for database use
        :return (dict): dictionary of patient data
        """
        deconstructed = {ModelPatient.KW_ID: self.ID,
                         ModelPatient.KW_NAME: self.name,
                         ModelPatient.KW_SURNAME: self.surname,
                         ModelPatient.KW_YEAR_OF_BIRTH: self.year_of_birth,
                         ModelPatient.KW_SEX: self.sex,
                         ModelPatient.KW_MEDIC_ID: self.medic_id
                         }
        if not self.safe_mode:
            deconstructed = {**deconstructed,
                             ModelPatient.KW_DIAGNOSIS: self.diagnosis,
                             ModelPatient.KW_MEDICAL_NOTES: self.medical_notes,
                             }

        filtered = {key: value for key, value in deconstructed.items()
                    if value not in [ModelPatient.V_EMPTY_STRING, ModelPatient.V_EMPTY_INT, ModelPatient.V_EMPTY_DICT]
                    }
        return dict(filtered)

    def add_original_image(self, image, image_data: dict) -> int:
        """
        Adds original image to database
        :param image: raw image data
        :param image_data: (dict) image data in form of dictionary
        :return: success code (0 on success, 1 on error)
        """
        image_data = {
            **image_data,
            "pacient_id": self.ID,
            "image": image
        }
        db = Database()
        success = db.insert_one_original_image(image_data)
        db.close()
        return success

    def search_original_images(self, condition: str, simplified: bool = True):
        """
        Searches for original images connected to this patient
        :parameter
         - condition: (str) SQL WHERE condition
         - simplified: (bool) if True, returns simplified list
        :return: (list) list of original images
        """
        db = Database()
        condition = f"pacient_id = {self.ID}" + ("" if condition == "" else " AND ")
        found_images = db.select_original_images(condition)
        db.close()
        if simplified:
            simplified_list = []
            for image in found_images:
                try:
                    simplified_list.append({
                        "id": image["id"],
                        "eye": image.get("oko", "nezadané")
                    })
                except KeyError:
                    continue
            return simplified_list
        else:
            return found_images

    def select_original_image(self, imageID) -> ["ModelOriginalImage", None]:
        """
        Selects original image with a given ID
        :param imageID: (int) ID of the original image
        :return: object of selected image or None
        """
        db = Database()
        condition = f"pacient_id = {self.ID} AND id = {imageID}"
        found = db.select_original_images(condition)
        db.close()
        try:
            return ModelOriginalImage.constructor(found[0])
        except IndexError:
            return None

    @staticmethod
    def send_image_for_processing(method_id: int, image: ModelOriginalImage):
        # TODO: needs processing received info
        ips = IPS()
        processed_image = ips.use_method(method_id, image)
        return processed_image

    def delete_selected_original_image(self, imageID):
        """
        Deletes an original image with a given ID, connected to this patient from the database.
        Deletes also connected processed images.

        Parameters:
        - imageID (int): ID of the image to be deleted

        Returns:
        - int: 0 on success, 1 on error
        """
        db = Database()
        condition = f"pacient_id = {self.ID} AND originalny_obraz_id = {imageID}"
        success = db.delete_original_images(condition)
        success |= db.delete_processed_images(condition)
        db.close()
        return success

    def search_processed_images(self, condition: str, simplified: bool = True):
        """
        Searches for processed images connected to this patient
        :param condition: (str) SQL WHERE condition
        :param simplified: (bool) if True, returns simplified list
        :return: (list) list of processed images
        """
        db = Database()
        condition = f"pacient_id = {self.ID}" + ("" if condition == "" else " AND ")
        found_images = db.select_processed_images(condition)
        db.close()
        if simplified:
            simplified_list = []
            for image in found_images:
                try:
                    simplified_list.append({
                        "id": image["id"],
                        "state": image.get("stav", "nezadané"),
                        "method_id": image.get("metoda_id", -1)
                    })
                except KeyError:
                    continue
            return simplified_list
        else:
            return found_images

    def select_processed_image(self, imageID) -> ["ModelProcessedImage", None]:
        """
        Selects processed image with a given ID
        :param imageID: (int) ID of the processed image
        :return: object of selected processed image or None
        """
        db = Database()
        condition = f"pacient_id = {self.ID} AND id = {imageID}"
        found = db.select_processed_images(condition)
        db.close()
        try:
            return ModelProcessedImage.constructor(found[0])
        except IndexError:
            return None

    def delete_selected_processed_image(self, imageID: int):
        """
        Deletes a processed image with a given ID, connected to this patient from the database.

        Parameters:
        - imageID (int): ID of the image to be deleted

        Returns:
        - int: 0 on success, 1 on error
        """
        db = Database()
        condition = f"pacient_id = {self.ID} AND id = {imageID}"
        success = db.delete_processed_images(condition)
        db.close()
        return success

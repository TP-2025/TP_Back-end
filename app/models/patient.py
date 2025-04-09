from app.database import Database
from app.models.original_image import OriginalImage
from app.models.processed_image import ProcessedImage
from app.services.image_processing_server import IPS


class Patient:
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
    def constructor(data: dict, safe_mode: bool) -> "Patient":
        """Function to construct Patient object from raw data in dictionary

        :param data: (dict) patient data
        :param safe_mode: (bool) loads only non-sensitive information
        :return: new Patient object
        """
        try:
            ID = data[Patient.KW_ID]
            medic_id = data[Patient.KW_MEDIC_ID]
        except KeyError:
            raise KeyError("Patient doesn't have ID or medic ID, it cannot be constructed")

        name = data.get(Patient.KW_NAME, Patient.V_EMPTY_STRING)
        surname = data.get(Patient.KW_SURNAME, Patient.V_EMPTY_STRING)
        year_of_birth = data.get(Patient.KW_YEAR_OF_BIRTH, Patient.V_EMPTY_INT)
        sex = data.get(Patient.KW_SEX, Patient.V_EMPTY_STRING)
        if safe_mode:
            diagnosis = Patient.V_EMPTY_STRING
            medical_notes = Patient.V_EMPTY_STRING
        else:
            diagnosis = data.get(Patient.KW_DIAGNOSIS, Patient.V_EMPTY_STRING)
            medical_notes = data.get(Patient.KW_MEDICAL_NOTES, Patient.V_EMPTY_STRING)
        return Patient(ID, name, surname, year_of_birth, sex, diagnosis, medical_notes, medic_id, safe_mode)

    def deconstructor(self) -> dict:
        """
        Function for deconstructing Patient object into dict for database use
        :return (dict): dictionary of patient data
        """
        deconstructed = {Patient.KW_ID: self.ID,
                         Patient.KW_NAME: self.name,
                         Patient.KW_SURNAME: self.surname,
                         Patient.KW_YEAR_OF_BIRTH: self.year_of_birth,
                         Patient.KW_SEX: self.sex,
                         Patient.KW_MEDIC_ID: self.medic_id
                         }
        if not self.safe_mode:
            deconstructed = {**deconstructed,
                             Patient.KW_DIAGNOSIS: self.diagnosis,
                             Patient.KW_MEDICAL_NOTES: self.medical_notes,
                             }

        filtered = {key: value for key, value in deconstructed.items()
                    if value not in [Patient.V_EMPTY_STRING, Patient.V_EMPTY_INT, Patient.V_EMPTY_DICT]
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
            "pacient_id": self.ID,
            **image_data,
            "image": image
        }
        db = Database()
        success = db.insert_one_original_image(image_data)
        db.close()
        return success

    def search_original_images(self, condition: str, simplified: bool = True):
        """
        Searches for original images connected to this patient
        :param condition: (str) SQL WHERE condition
        :param simplified: (bool) if True, returns simplified list
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

    def select_original_image(self, imageID) -> ["OriginalImage", None]:
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
            return OriginalImage.constructor(found[0])
        except IndexError:
            return None

    @staticmethod
    def send_image_for_processing(method_id: int, image: OriginalImage):
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

    def select_processed_image(self, imageID) -> ["ProcessedImage", None]:
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
            return ProcessedImage.constructor(found[0])
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

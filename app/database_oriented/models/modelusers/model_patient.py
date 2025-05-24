from app.database_oriented.database import Database
from app.database_oriented.exitcodes_errors import ExitCodes
from app.database_oriented.models.modelimages.model_original_image import ModelOriginalImage
from app.database_oriented.models.modelimages.model_processed_image import ModelProcessedImage
import app.database_oriented.keywords as kw

from app.database_oriented.models.modelusers.model_user import ModelUser


class ModelPatient(ModelUser):

    def __init__(self, ID: int, patient_id: int, diagnosis: str, medical_notes: str,
                 medic_id: int, safe_mode: bool, **kwargs):
        role_id = Database.get_role_id_by_name(kw.ROLE_PATIENT)

        name = kwargs.pop(kw.KW_USER_NAME, kw.V_EMPTY_STRING)
        surname = kwargs.pop(kw.KW_USER_SURNAME, kw.V_EMPTY_STRING)
        date_of_birth = kwargs.pop(kw.KW_PATIENT_DATE_OF_BIRTH, kw.V_EMPTY_STRING)

        super().__init__(ID, name, surname, 0, role_id, **kwargs)
        self.patient_id = patient_id
        self.date_of_birth = date_of_birth
        self.diagnosis = diagnosis
        self.medical_notes = medical_notes
        self.medic_id = medic_id
        self.safe_mode = safe_mode

    @classmethod
    def constructor(cls, data: dict) -> "ModelPatient":
        """Function to construct ModelPatient object from raw data in dictionary

        :param data: (dict) patient data + safe_mode(bool - loads only non-sensitive information)
        :return: new ModelPatient object
        :raise KeyError: if patient doesn't have ID, patient ID or medic id
        """
        try:
            ID = data.pop(kw.KW_USER_ID, -2222)
            patient_id = data.pop(kw.KW_PATIENT_ID, -2222)
            medic_id = data.pop(kw.KW_PATIENT_MEDIC_ID, -2222)
            safe_mode = data.pop("safe_mode", False)
            if -2222 in [ID, patient_id, medic_id]:
                raise KeyError
        except KeyError:
            raise KeyError("ModelPatient doesn't have ID or medic id, it cannot be constructed")

        if safe_mode:
            data.pop(kw.KW_PATIENT_DIAGNOSIS, None)
            data.pop(kw.KW_PATIENT_NOTE_MEDIC, None)

        diagnosis = data.pop(kw.KW_PATIENT_DIAGNOSIS, kw.V_EMPTY_STRING)
        medical_notes = data.pop(kw.KW_PATIENT_NOTE_MEDIC, kw.V_EMPTY_STRING)

        return cls(ID, patient_id, diagnosis, medical_notes, medic_id, safe_mode, **data)

    def deconstructor(self) -> dict:
        """
        Function for deconstructing ModelPatient object into dict for database use
        :return (dict): dictionary of patient data
        """
        deconstructed = {
                         **super().deconstructor(),
                         kw.KW_PATIENT_ID: self.patient_id,
                         kw.KW_PATIENT_DATE_OF_BIRTH: self.date_of_birth,
                         kw.KW_PATIENT_MEDIC_ID: self.medic_id
                         }
        if not self.safe_mode:
            deconstructed = {**deconstructed,
                             kw.KW_PATIENT_DIAGNOSIS: self.diagnosis,
                             kw.KW_PATIENT_NOTE_MEDIC: self.medical_notes,
                             }

        filtered = {key: value for key, value in deconstructed.items()
                    if value not in [kw.V_EMPTY_STRING, kw.V_EMPTY_INT, kw.V_EMPTY_DICT]
                    }
        return dict(filtered)

    @staticmethod
    def get_patient_by_patient_id(patient_id: int) -> ["ModelPatient", None]:
        """
        Function for getting patient object by patient_id
        :param patient_id: (int) patient ID
        :return: (ModelPatient, None) patient object if found or None
        """
        db = Database()
        patient = db.get_patients(patient_id)
        db.close()

        try:
            return ModelPatient.constructor(patient[0])
        except IndexError:
            return None

    def add_original_image(self, image_data: dict) -> int:
        """
        Adds original image to database
        :param image_data: (dict) dictionary of original image data
        :return: (int) exit code
        """
        image_data = {
            **image_data,
            kw.KW_PATIENT_ID: self.patient_id,
        }
        exit_code, self.selected_image = ModelOriginalImage.add_original_image(image_data)
        return exit_code

    def get_original_images(self, simplified: bool = False) -> list[dict]:
        """
        Returns list of original images connected to this patient
        :param simplified: (bool) if True, returns simplified list of original images
        :return: (list[dict]) list of original images
        """
        images = self.search_original_images("", simplified)
        return images

    @staticmethod
    def get_original_image_model_by_id(image_id: int) -> ["ModelOriginalImage", None]:
        """
        Returns original image model by ID
        :param image_id: (int) ID of original image
        :return: (ModelOriginalImage) original image model if found or None
        """
        try:
            return ModelOriginalImage.get_original_image_by_id(image_id)
        except IndexError:
            return None

    def delete_me(self) -> int:
        """Deletes patient and all of its data from database
        :return: (int) exit code
        """
        db = Database()
        exit_code = db.delete_patients(f"{kw.KW_PATIENT_ID} = {self.patient_id}")
        exit_code |= db.delete_users(f"{kw.KW_USER_ID} = {self.ID}")
        exit_code |= db.close()
        return exit_code

    def search_original_images(self, condition: str, simplified: bool = False):
        """
        Searches for processed images connected to this patient
        :param condition: (str) SQL WHERE condition
        :param simplified: (bool) if True, returns simplified list
        :return: (list) list of processed images
        """
        condition = f"{kw.KW_IMAGE_PATIENT_ID} = {self.patient_id}" + ("" if condition == "" else " AND ") + condition
        return ModelOriginalImage.search_original_images(condition, simplified)

    @staticmethod
    def send_image_for_processing(image_model: ModelOriginalImage, additional_data: dict) -> (int, ModelProcessedImage):
        """
        Adds processed image to database (making from original image processed)
        :param image_model: (ModelOriginalImage) original image model
        :param additional_data: (dict) additional data for processed image
        :return: (int, ModelProcessedImage) exit code and processed image model
        """
        return image_model.send_image_for_processing(additional_data)

    @staticmethod
    def multi_send_image_for_processing(image_models: list, additional_data_list: list) -> (int, list[int]):
        """
        Adds processed images to database (making from original images processed)
        :param image_models: (list) list of original image models
        :param additional_data_list: (list) list of additional data for processed images
        :return: (int, list) exit code and list of processed image IDs
        """
        exit_code = ExitCodes.SUCCESS
        IDs = []
        for image_model, additional_data in zip(image_models, additional_data_list):
            ec, image = image_model.send_image_for_processing(image_model, additional_data)
            exit_code |= ec
            IDs.append(image.ID)

        return exit_code, IDs

    def delete_original_image_by_id(self, imageID, wrapped: Database = None):
        """
        Deletes an original image with a given ID, connected to this patient from the database.
        Deletes also connected processed images.

        Parameters:
        - imageID (int): ID of the image to be deleted
        - wrapped (Database, optional): database object for making it more effective

        Returns:
        - int: Exit code
        """
        success = ExitCodes.SUCCESS
        if wrapped is not None:
            db = wrapped
        else:
            db = Database()

        condition_o = f"{kw.KW_IMAGE_PATIENT_ID} = {self.patient_id} AND {kw.KW_IMAGE_ID} = {imageID}"
        condition_p = f"{kw.KW_PIMAGE_OIMAGE_ID} = {imageID}"
        if len(db.select_original_images(condition_o)):
            success |= db.delete_processed_images(condition_p)
            success |= db.delete_original_images(condition_o)

        if wrapped is None:
            db.close()

        return success

    def multi_delete_original_image(self, imageIDs: list) -> int:
        """
        Deletes a processed image with a given ID, connected to this patient from the database
        :param imageIDs: (list[int, ...]) list of IDs of the processed images to be deleted
        :return: (int) exit code
        """
        success = ExitCodes.SUCCESS
        db = Database()
        for imageID in imageIDs:
            success |= self.delete_original_image_by_id(imageID, db)
        db.close()
        return success

    def get_processed_images(self) -> list[dict]:
        """
        Gets all processed images connected to this patient
        :return: (list[dict]) list of processed images
        """
        return ModelProcessedImage.get_processed_images(patient_id=self.patient_id)

    def search_processed_images(self, condition: str, simplified: bool = True) -> list[dict]:
        """
        Searches for processed images connected to this patient
        :param condition: (str) SQL WHERE condition
        :param simplified: (bool) if True, returns simplified list
        :return: (list) list of processed images
        """
        condition = f"{kw.KW_PIMAGE_PATIENT_ID} = {self.patient_id}" + ("" if condition == "" else " AND ") + condition
        return ModelProcessedImage.search_processed_images(condition, simplified)

    @staticmethod
    def get_processed_image_by_id(imageID: int) -> ["ModelProcessedImage", None]:
        """
        Selects processed image with a given ID
        :param imageID: (int) ID of the processed image
        :return: object of selected processed image if found or None
        """
        try:
            return ModelProcessedImage.get_processed_image_by_id(imageID)
        except IndexError:
            return None

    def delete_processed_image_by_id(self, imageID: int, wrapped: Database = None) -> int:
        """
        Deletes a processed image with a given ID, connected to this patient from the database
        :parameter
         - imageID: (int) ID of the processed image to be deleted
         - wrapped: (Database, optional) database to use for more effective approach
        :return: (int) Exit code
        """
        if wrapped is not None:
            db = wrapped
        else:
            db = Database()

        condition = f"{kw.KW_PATIENT_ID} = {self.patient_id} AND {kw.KW_PIMAGE_ID} = {imageID}"
        success = db.delete_processed_images(condition)

        if wrapped is None:
            db.close()

        return success

    def multi_delete_processed_image(self, imageIDs: list) -> int:
        """
        Deletes a processed image with a given ID, connected to this patient from the database
        :param imageIDs: (list[int, ...]) list of IDs of the processed images to be deleted
        :return: (int) Exit code
        """
        success = ExitCodes.SUCCESS
        db = Database()
        for imageID in imageIDs:
            success |= self.delete_processed_image_by_id(imageID)
        db.close()
        return success

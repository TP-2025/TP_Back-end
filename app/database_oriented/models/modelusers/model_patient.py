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
                         kw.KW_PATIENT_ID: self.ID,
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
    def get_patient_by_patient_id(patient_id: int):
        db = Database()
        patient = db.get_patients(patient_id)
        db.close()

        try:
            return ModelPatient.constructor(patient[0])
        except IndexError:
            return None

    def add_original_image(self, image_data: dict) -> int:
        image_data = {
            **image_data,
            kw.KW_PATIENT_ID: self.patient_id,
        }
        exit_code, self.selected_image = ModelOriginalImage.add_original_image(image_data)
        return exit_code

    def get_original_images(self):
        images = self.search_original_images("", False)
        return images

    # def get_processed_images(self):
    #     images = self.search_processed_images("", False)
    #     return images

    def delete_me(self):
        """Deletes patient and all of its data from database"""
        db = Database()
        db.delete_patients(f"{kw.KW_PATIENT_ID} = {self.patient_id}")
        db.delete_users(f"{kw.KW_USER_ID} = {self.ID}")
        db.close()

    def search_original_images(self, condition: str, simplified: bool = False):
        """
        Searches for processed images connected to this patient
        :param condition: (str) SQL WHERE condition
        :param simplified: (bool) if True, returns simplified list
        :return: (list) list of processed images
        """
        condition = f"{kw.KW_IMAGE_PATIENT_ID} = {self.patient_id}" + ("" if condition == "" else " AND ") + condition
        return ModelOriginalImage.search_original_images(condition, simplified)

    # @staticmethod
    # def select_original_image_by_id(imageID: int) -> ["ModelProcessedImage", None]:
    #     """
    #     Selects processed image with a given ID
    #     :param imageID: (int) ID of the processed image
    #     :return: object of selected processed image or None
    #     """
    #     try:
    #         return ModelOriginalImage.get_original_image_by_id(imageID)
    #     except IndexError:
    #         return None

    @staticmethod
    def send_image_for_processing(image_model: ModelOriginalImage, additional_data: dict) -> (int, ModelProcessedImage):
        return image_model.send_image_for_processing(additional_data)

    @staticmethod
    def multi_send_image_for_processing(image_models: list, additional_data_list: list) -> int:
        exit_code = ExitCodes.SUCCESS
        for image_model, additional_data in zip(image_models, additional_data_list):
            ec, _ = image_model.send_image_for_processing(image_model, additional_data)
            exit_code |= ec

        return exit_code

    def delete_original_image_by_id(self, imageID, wrapped: Database = None):
        """
        Deletes an original image with a given ID, connected to this patient from the database.
        Deletes also connected processed images.

        Parameters:
        - imageID (int): ID of the image to be deleted

        Returns:
        - int: 0 on success, 1 on error
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

    def multi_delete_original_image(self, imageIDs: list):
        success = ExitCodes.SUCCESS
        db = Database()
        for imageID in imageIDs:
            success |= self.delete_original_image_by_id(imageID, db)
        db.close()

    # def search_processed_images(self, condition: str, simplified: bool = True):
    #     """
    #     Searches for processed images connected to this patient
    #     :param condition: (str) SQL WHERE condition
    #     :param simplified: (bool) if True, returns simplified list
    #     :return: (list) list of processed images
    #     """
    #     condition = f"{kw.KW_PIMAGE_PATIENT_ID} = {self.ID}" + ("" if condition == "" else " AND ") + condition
    #     return ModelProcessedImage.search_processed_images(condition, simplified)
    #
    # @staticmethod
    # def select_processed_image_by_id(imageID: int) -> ["ModelProcessedImage", None]:
    #     """
    #     Selects processed image with a given ID
    #     :param imageID: (int) ID of the processed image
    #     :return: object of selected processed image or None
    #     """
    #     try:
    #         return ModelProcessedImage.get_processed_image_by_id(imageID)
    #     except IndexError:
    #         return None

    # @staticmethod
    # def delete_processed_image_by_id(imageID: int, wrapped: Database = None):
    #     """
    #     Deletes a processed image with a given ID, connected to this patient from the database.
    #
    #     Parameters:
    #     - imageID (int): ID of the image to be deleted
    #
    #     Returns:
    #     - int: 0 on success, 1 on error
    #     """
    #     if wrapped is not None:
    #         db = wrapped
    #     else:
    #         db = Database
    #
    #     try:
    #         found = db.select_processed_images(f"id = {imageID}")
    #     except IndexError:
    #         raise IndexError(f"Processed image with given ID '{imageID}' not found")
    #
    #
    #     condition = f"{kw.KW_PATIENT_ID} = {self.ID} AND id = {imageID}"
    #     success = db.delete_processed_images(condition)
    #
    #     if wrapped is None:
    #         db.close()
    #
    #     return success
    #
    # def multi_delete_processed_image(self, imageIDs: list):
    #     success = ExitCodes.SUCCESS
    #     db = Database()
    #     for imageID in imageIDs:
    #         success |= self.delete_processed_image_by_id(imageID)
    #     db.close()

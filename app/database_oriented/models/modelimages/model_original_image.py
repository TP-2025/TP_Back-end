import random

from app.database_oriented.database import Database
from app.database_oriented.models.modelimages.model_processed_image import ModelProcessedImage
import app.database_oriented.keywords as kw


class ModelOriginalImage:
    def __init__(self, ID: int, patient_id: int, device_id: int, path_to_image: str, quality: str, eye: str,
                 technic_notes: str, diagnosis_notes: str, safe_mode: bool):
        self.ID = ID
        self.patient_id = patient_id
        self.device_id = device_id
        self.path_to_image = path_to_image
        self.quality = quality
        self.eye = eye
        self.path_to_image = path_to_image
        self.technic_notes = technic_notes
        self.diagnosis_notes = diagnosis_notes
        self.safe_mode = safe_mode

    @staticmethod
    def constructor(data: dict, safe_mode: bool = False) -> "ModelOriginalImage":
        """
        Constructs ModelOriginalImage object from raw data from database
        :param data: (dict) original image data from database
        :param safe_mode: (bool) loads only non-sensitive information
        :return: (ModelOriginalImage) new ModelOriginalImage object
        :raise KeyError: if original image doesn't have ID or patient ID
        """
        try:
            ID = data[kw.KW_IMAGE_ID]
            patient_id = data[kw.KW_PATIENT_ID]
        except KeyError:
            raise KeyError("Original image doesn't have ID or patient ID, it cannot be constructed")
        device_id = data.get(kw.KW_DEVICE_ID, kw.V_EMPTY_INT)
        path_to_image = data.get(kw.KW_IMAGE_PATH, kw.V_EMPTY_STRING)
        quality = data.get(kw.KW_IMAGE_QUALITY, kw.V_EMPTY_STRING)
        eye = data.get(kw.KW_IMAGE_EYE, kw.V_EMPTY_STRING)
        if safe_mode:
            technic_notes = kw.V_EMPTY_STRING
            diagnosis_notes = kw.V_EMPTY_STRING
        else:
            technic_notes = data.get(kw.KW_IMAGE_NOTE_TECHNIC, kw.V_EMPTY_STRING)
            diagnosis_notes = data.get(kw.KW_IMAGE_NOTE_DIAGNOSIS, kw.V_EMPTY_STRING)

        return ModelOriginalImage(ID, patient_id, device_id, path_to_image, quality, eye,
                                  technic_notes, diagnosis_notes, safe_mode)

    def deconstructor(self) -> dict:
        """
        Deconstructs ModelOriginalImage object to dictionary
        :return: (dict) dictionary of original image data
        """
        deconstructed = {kw.KW_IMAGE_ID: self.ID,
                         kw.KW_PATIENT_ID: self.patient_id,
                         kw.KW_DEVICE_ID: self.device_id,
                         kw.KW_IMAGE_PATH: self.path_to_image,
                         kw.KW_IMAGE_QUALITY: self.quality,
                         kw.KW_IMAGE_EYE: self.eye
                         }
        if not self.safe_mode:
            deconstructed = {**deconstructed,
                             kw.KW_IMAGE_NOTE_TECHNIC: self.technic_notes,
                             kw.KW_IMAGE_NOTE_DIAGNOSIS: self.diagnosis_notes,
                             }

        filtered = {key: value for key, value in deconstructed.items()
                    if value not in [kw.V_EMPTY_STRING, kw.V_EMPTY_INT, kw.V_EMPTY_DICT]
                    }
        return dict(filtered)

    @staticmethod
    def add_original_image(image_data: dict) -> (int, "ModelOriginalImage"):
        """
        Adds original image to database
        :param image_data: (dict) dictionary of original image data
        :returns: (int, ModelOriginalImage) exit code and original image object
        :raise
        - KeyError: if original image doesn't have path or patient ID
        """
        required_keys = (kw.KW_IMAGE_PATH, kw.KW_IMAGE_PATIENT_ID)
        for key in required_keys:
            if key not in image_data.keys():
                raise KeyError(f"Key '{key}' is required for patient creation")

        image_data[kw.KW_IMAGE_ID] = kw.V_EMPTY_INT
        image_model = ModelOriginalImage.constructor(image_data)
        all_data = image_model.deconstructor()

        db = Database()
        exit_code = db.insert_one_original_image(all_data)
        db.close()

        return exit_code, image_model

    @classmethod
    def get_original_image_by_id(cls, image_id: int, safe_mode: bool = False) -> "ModelOriginalImage":
        """
        Gets original image by ID
        :param image_id: (int) ID of original image to get
        :param safe_mode: (bool) loads only non-sensitive information
        :return: (ModelOriginalImage) object of ModelOriginalImage
        :raise IndexError: if original image with given ID doesn't exist
        """
        db = Database()
        found = db.select_original_images(f"id = {image_id}")
        db.close()
        try:
            return cls.constructor(found[0], safe_mode)
        except IndexError:
            raise IndexError(f"Original image with given ID '{image_id}' not found")

    @staticmethod
    def delete_original_image_by_id(image_id: int) -> int:
        """
        Deletes original image by ID
        :param image_id: (int) ID of original image to delete
        :return: (int) exit code
        """
        db = Database()
        exit_code = db.delete_original_images(f"{kw.KW_IMAGE_ID} = {image_id}")
        db.close()
        return exit_code

    def delete_me(self) -> int:
        """
        Deletes original image from database
        :return: (int) exit code
        """
        return self.delete_original_image_by_id(self.ID)

    @staticmethod
    def search_original_images(condition: str, simplified: bool = True) -> list:
        """
        Searches for original images in database for which MySQL condition is true
        :parameter
         - condition: (str) SQL WHERE condition
         - simplified: (bool) if True, returns simplified list
        :return: (list) list of original images
        """
        db = Database()
        found_images = db.select_original_images(condition)
        if simplified:
            simplified_list = []
            for image in found_images:
                try:
                    simplified_list.append({
                        kw.KW_IMAGE_ID: image[kw.KW_IMAGE_ID],
                        kw.KW_IMAGE_EYE: image.get(kw.KW_IMAGE_EYE, "nezadané"),
                        "processed_images": db.count_processed_images(f"{kw.KW_PIMAGE_OIMAGE_ID} = {image[kw.KW_IMAGE_ID]}")
                    })
                except KeyError:
                    continue
            db.close()
            return simplified_list
        else:
            db.close()
            return found_images

    def send_image_for_processing(self, additional_data: dict) -> (int, "ModelProcessedImage"):
        """
        Sends original image for processing
        :param additional_data: (dict) dictionary of additional data for processed image
        :return: (int, ModelProcessedImage) exit code and processed image object
        """
        all_data = {**additional_data, kw.KW_PIMAGE_ID: kw.V_EMPTY_INT,
                    kw.KW_PIMAGE_OIMAGE_ID: self.ID, kw.KW_PIMAGE_EYE: self.eye}

        exit_code, model_pimage = ModelProcessedImage.add_processed_image(all_data)

        return exit_code, model_pimage

    def get_processed_images(self) -> list[dict]:
        """
        Gets all processed images connected to this original image
        :return: (list[dict]) list of processed images
        """
        return ModelProcessedImage.get_processed_images(oimage_id=self.ID)

    def search_processed_images(self, condition: str, simplified: bool = True) -> list[dict]:
        """
        Searches for processed images connected to this patient for which MySQL condition is true
        :param condition: (str) SQL WHERE condition
        :param simplified: (bool) if True, returns simplified list
        :return: (list[dict]) list of processed images
        """
        condition = f"{kw.KW_PIMAGE_OIMAGE_ID} = {self.ID}" + ("" if condition == "" else " AND ") + condition
        return ModelProcessedImage.search_processed_images(condition, simplified)

    @staticmethod
    def select_processed_image_by_id(imageID: int) -> ["ModelProcessedImage", None]:
        """
        Selects processed image with a given ID
        :param imageID: (int) ID of the processed image
        :return: object of selected processed image or None
        """
        try:
            return ModelProcessedImage.get_processed_image_by_id(imageID)
        except IndexError:
            return None

    def delete_all_connected_processed_images(self) -> int:
        """
        Deletes all processed images connected to this original image from the database.

        Returns:
        - int: exit code
        """
        db = Database()
        condition = f"{kw.KW_PIMAGE_OIMAGE_ID} = {self.ID}"
        success = db.delete_processed_images(condition)
        db.close()
        return success

    @staticmethod
    def delete_processed_image_by_id(processed_imageID):
        """
        Deletes a processed image with a given ID, connected to this original image from the database.

        Parameters:
        - imageID (int): ID of the image to be deleted

        Returns:
        - int: Exit code
        """
        return ModelProcessedImage.delete_processed_image_by_id(processed_imageID)

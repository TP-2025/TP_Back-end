from app.database_oriented.database import Database
from app.database_oriented.models.model_processed_image import ModelProcessedImage


class ModelOriginalImage:
    # Keywords for accessing processed image data in database
    KW_ID = "id"
    KW_PATIENT_ID = "pacient_id"
    KW_DEVICE_ID = "zariadenie_id"
    KW_PATH_TO_IMAGE = "cesta"
    KW_QUALITY = "kvalita"
    KW_EYE = "oko"
    KW_TECHNIC_NOTES = "poznamka_technika"
    KW_DIAGNOSIS_NOTES = "poznamka_diagnoza"

    # Default values of empty fields
    V_EMPTY_STRING = "Nothing here"
    V_EMPTY_INT = -1111
    V_EMPTY_DICT = {"empty": "empty"}

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
        """
        try:
            ID = data[ModelOriginalImage.KW_ID]
            patient_id = data.get(ModelOriginalImage.KW_PATIENT_ID, ModelOriginalImage.V_EMPTY_INT)
        except KeyError:
            raise KeyError("Original image doesn't have ID or patient ID, it cannot be constructed")
        device_id = data.get(ModelOriginalImage.KW_DEVICE_ID, ModelOriginalImage.V_EMPTY_INT)
        path_to_image = data.get(ModelOriginalImage.KW_PATH_TO_IMAGE, ModelOriginalImage.V_EMPTY_STRING)
        quality = data.get(ModelOriginalImage.KW_QUALITY, ModelOriginalImage.V_EMPTY_STRING)
        eye = data.get(ModelOriginalImage.KW_EYE, ModelOriginalImage.V_EMPTY_STRING)
        if safe_mode:
            technic_notes = ModelOriginalImage.V_EMPTY_STRING
            diagnosis_notes = ModelOriginalImage.V_EMPTY_STRING
        else:
            technic_notes = data.get(ModelOriginalImage.KW_TECHNIC_NOTES, ModelOriginalImage.V_EMPTY_STRING)
            diagnosis_notes = data.get(ModelOriginalImage.KW_DIAGNOSIS_NOTES, ModelOriginalImage.V_EMPTY_STRING)

        return ModelOriginalImage(ID, patient_id, device_id, path_to_image, quality, eye,
                                  technic_notes, diagnosis_notes, safe_mode)

    def deconstructor(self) -> dict:
        """
        Deconstructs ModelOriginalImage object to dictionary
        :return: (dict) dictionary of original image data
        """
        deconstructed = {ModelOriginalImage.KW_ID: self.ID,
                         ModelOriginalImage.KW_PATIENT_ID: self.patient_id,
                         ModelOriginalImage.KW_DEVICE_ID: self.device_id,
                         ModelOriginalImage.KW_PATH_TO_IMAGE: self.path_to_image,
                         ModelOriginalImage.KW_QUALITY: self.quality,
                         ModelOriginalImage.KW_EYE: self.eye
                         }
        if not self.safe_mode:
            deconstructed = {**deconstructed,
                             ModelOriginalImage.KW_TECHNIC_NOTES: self.technic_notes,
                             ModelOriginalImage.KW_DIAGNOSIS_NOTES: self.diagnosis_notes,
                             }

        filtered = {key: value for key, value in deconstructed.items()
                    if value not in [ModelOriginalImage.V_EMPTY_STRING, ModelOriginalImage.V_EMPTY_INT, ModelOriginalImage.V_EMPTY_DICT]
                    }
        return dict(filtered)

    # TODO: Find out specific format for image raw data and use it with the get_image method
    def get_image(self):  # raw data of image in not yet specified format
        return self.path_to_image  # need for returning the right format of image

    def search_processed_images(self, condition: str, simplified: bool = True) -> list:
        """
        Returns list of ModelProcessedImage objects from database
        :param condition: (str) SQL WHERE condition
        :param simplified: (bool) if True, returns simplified list
        :return: (list) list of rows from database that fulfill condition
        """
        db = Database()
        condition = f"{ModelProcessedImage.KW_PATIENT_ID} = {self.patient_id} AND {ModelProcessedImage.KW_ORIGINAL_IMAGE_ID} = {self.ID}" + (
            "" if condition == "" else " AND ")
        found_images = db.select_processed_images(condition)
        db.close()
        if simplified:
            simplified_list = []
            for image in found_images:
                try:
                    simplified_list.append({
                        ModelProcessedImage.KW_ID: image[ModelProcessedImage.KW_ID],
                        ModelProcessedImage.KW_STATE: image.get(ModelProcessedImage.KW_STATE, "nezadané"),
                        ModelProcessedImage.KW_USED_METHOD_ID: image.get(ModelProcessedImage.KW_USED_METHOD_ID, ModelProcessedImage.V_EMPTY_INT)
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
        :return: [ModelProcessedImage, None] object of selected processed image or None
        """
        db = Database()
        condition = f"{ModelProcessedImage.KW_PATIENT_ID} = {self.patient_id} AND {ModelProcessedImage.KW_ORIGINAL_IMAGE_ID} = {self.ID} AND {ModelProcessedImage.KW_ID} = {imageID}"
        found = db.select_processed_images(condition)
        db.close()
        try:
            return ModelProcessedImage.constructor(found[0])
        except IndexError:
            return None

    def delete_all_connected_processed_images(self):
        """
        Deletes all processed images connected to this original image from the database.

        Returns:
        - int: 0 on success, 1 on error
        """
        db = Database()
        condition = f"{ModelProcessedImage.KW_PATIENT_ID} = {self.patient_id} AND {ModelProcessedImage.KW_ORIGINAL_IMAGE_ID} = {self.ID}"
        success = db.delete_processed_images(condition)
        db.close()
        return success

    def delete_selected_processed_image(self, imageID):
        """
        Deletes a processed image with a given ID, connected to this original image from the database.

        Parameters:
        - imageID (int): ID of the image to be deleted

        Returns:
        - int: 0 on success, 1 on error
        """
        db = Database()
        condition = f"{ModelProcessedImage.KW_PATIENT_ID} = {self.patient_id} AND {ModelProcessedImage.KW_ORIGINAL_IMAGE_ID} = {self.ID} AND {ModelProcessedImage.KW_ID} = {imageID}"
        success = db.delete_processed_images(condition)
        db.close()
        return success

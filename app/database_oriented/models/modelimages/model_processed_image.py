import app.database_oriented.keywords as kw
from app.database_oriented.database import Database
from app.database_oriented.exitcodes_errors import ExitCodes


class ModelProcessedImage:
    KW_RAW_IMAGE = "obraz"

    def __init__(self, ID: int, original_image_id: int, used_method_id: int,
                 results: dict, path_to_image: str, state: str, eye: str):
        self.ID = ID
        self.original_image_id = original_image_id
        self.used_method_id = used_method_id
        self.used_method_name = Database.get_method_by_id(used_method_id)
        self.results = results
        self.path_to_image = path_to_image
        self.state = state
        self.eye = eye

    @staticmethod
    def constructor(data: dict) -> "ModelProcessedImage":
        """
        Constructs ModelProcessedImage object from raw data
        :param data: (dict) image data from database
        :return: (ModelProcessedImage) object of ModelProcessedImage
        """
        try:
            ID = data[kw.KW_PIMAGE_ID]
            original_image_id = data[kw.KW_PIMAGE_OIMAGE_ID]
            used_method_id = data[kw.KW_PIMAGE_USED_METHOD_ID]
        except KeyError:
            raise KeyError("Processed image doesn't have ID or original image ID, it cannot be constructed")

        results = data.get(kw.KW_PIMAGE_RESULTS, kw.V_EMPTY_DICT)
        path_to_image = data.get(kw.KW_PIMAGE_PATH, kw.V_EMPTY_STRING)
        state = data.get(kw.KW_PIMAGE_STATE, kw.KW_PIMAGE_STATE)
        eye = data.get(kw.KW_PIMAGE_EYE, kw.V_EMPTY_STRING)
        return ModelProcessedImage(ID, original_image_id, used_method_id, results, path_to_image, state, eye)

    def deconstructor(self) -> dict:
        """
        Deconstructs ModelProcessedImage object into dictionary
        :return: (dict) dictionary of processed image data
        """
        deconstructed = {
            kw.KW_PIMAGE_ID: self.ID,
            kw.KW_PIMAGE_OIMAGE_ID: self.original_image_id,
            kw.KW_PIMAGE_USED_METHOD_ID: self.used_method_id,
            kw.KW_PIMAGE_RESULTS: self.results,
            kw.KW_PIMAGE_PATH: self.path_to_image,
            # ModelProcessedImage.KW_RAW_IMAGE: self.raw_image,
            kw.KW_PIMAGE_STATE: self.state,
            kw.KW_PIMAGE_EYE: self.eye
        }

        filtered = {key: value for key, value in deconstructed.items()
                    if value not in [kw.V_EMPTY_STRING, kw.V_EMPTY_INT,
                                     kw.V_EMPTY_DICT]
                    }
        return dict(filtered)

    @staticmethod
    def add_processed_image(image_data: dict) -> (int, "ModelProcessedImage"):
        required_keys = (kw.KW_METHOD_ID, kw.KW_PIMAGE_OIMAGE_ID)  # ,kw.KW_PIMAGE_PATH)
        for key in required_keys:
            if key not in image_data.keys():
                raise KeyError(f"Key '{key}' is required for processed image creation")

        image_data[kw.KW_IMAGE_ID] = kw.V_EMPTY_INT
        image_model = ModelProcessedImage.constructor(image_data)
        all_data = image_model.deconstructor()

        db = Database()
        exit_code = db.insert_one_processed_image(all_data)
        db.close()

        return exit_code, image_model

    @classmethod
    def get_processed_image_by_id(cls, image_id: int) -> "ModelProcessedImage":
        db = Database()
        found = db.get_users(image_id)
        db.close()

        try:
            return cls.constructor(found[0])
        except IndexError:
            raise IndexError(f"Processed image with given ID '{image_id}' not found")

    @staticmethod
    def delete_processed_image_by_id(image_id: int):
        db = Database()
        exit_code = db.delete_processed_images(f"{kw.KW_PIMAGE_ID} = {image_id}")
        db.close()
        return exit_code

    @staticmethod
    def multi_delete_processed_images(image_ids: list):
        success = ExitCodes.SUCCESS
        db = Database()
        for image_id in image_ids:
            success |= ModelProcessedImage.delete_processed_image_by_id(image_id)
        db.close()
        return success

    def delete_me(self):
        """Deletes processed image from database"""
        return self.delete_processed_image_by_id(self.ID)

    @staticmethod
    def search_processed_images(condition: str, simplified: bool = True):
        """
        Searches for processed images connected to this patient
        :param condition: (str) SQL WHERE condition
        :param simplified: (bool) if True, returns simplified list
        :return: (list) list of processed images
        """
        db = Database()
        found_images = db.select_processed_images(condition)
        db.close()
        if simplified:
            simplified_list = []
            for image in found_images:
                try:
                    simplified_list.append({
                        kw.KW_PIMAGE_ID: image[kw.KW_PIMAGE_ID],
                        kw.KW_PIMAGE_STATE: image.get(kw.KW_PIMAGE_STATE, "nezadané"),
                        kw.KW_PIMAGE_USED_METHOD_ID: image.get(kw.KW_PIMAGE_USED_METHOD_ID, -1)
                    })
                except KeyError:
                    continue
            return simplified_list
        else:
            return found_images

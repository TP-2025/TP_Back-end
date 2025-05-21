from app.database_oriented.models.modelimages.model_original_image import ModelOriginalImage
from app.database_oriented.models.modelimages.model_processed_image import ModelProcessedImage


class IPS:
    def __init__(self):
        self.connection = None

    def is_ready(self) -> bool:
        return self.connection is not None

    def use_method(self, method_id, image: ModelOriginalImage) -> ModelProcessedImage:
        try:
            get_method_json(method_id)
            image_raw = image.get_image()
            self.connection.use_method(method_id, image)
        except NotImplementedError:
            print("Connection not implemented yet")
        except Exception as e:
            raise e

    def close(self):
        try:
            self.connection.close()
        except NotImplementedError:
            print("Connection not implemented yet")
        except Exception as e:
            raise e


from app.models.original_image import OriginalImage
from app.models.processed_image import ProcessedImage


class IPS:
    def __init__(self):
        self.connection = None

    def is_ready(self) -> bool:
        return self.connection is not None

    def use_method(self, method_id, image: OriginalImage) -> ProcessedImage:
        try:
            image_raw = image.get_image()
            self.connection.use_method(method_id, image)
        except NotImplementedError:
            print("Connection not implemented yet")
        except Exception as e:
            raise e


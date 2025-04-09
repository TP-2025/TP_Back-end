class ProcessedImage:
    # Keywords for accessing processed image data in database
    KW_ID = "id"
    KW_PATIENT_ID = "pacient_id"
    KW_ORIGINAL_IMAGE_ID = "originaly_obraz_id"
    KW_USED_METHOD_ID = "metoda_id"
    KW_RESULTS = "vysledky"
    KW_PATH_TO_IMAGE = "cesta_k_obrazu"
    KW_RAW_IMAGE = "obraz"
    KW_STATE = "stav"

    # Default values of empty fields
    V_EMPTY_STRING = "Nothing here"
    V_EMPTY_INT = -1111
    V_EMPTY_DICT = {"empty": "empty"}

    def __init__(self, ID: int, patient_id: int, original_image_id: int, used_method_id: int,
                 results: dict, path_to_image: str, raw_image, state: str):
        self.ID = ID
        self.patient_id = patient_id
        self.original_image_id = original_image_id
        self.used_method_id = used_method_id
        self.results = results
        self.path_to_image = path_to_image
        self.raw_image = raw_image
        self.state = state

    @staticmethod
    def constructor(data: dict) -> "ProcessedImage":
        """
        Constructs ProcessedImage object from raw data
        :param data: (dict) image data from database
        :return: (ProcessedImage) object of ProcessedImage
        """
        try:
            ID = data[ProcessedImage.KW_ID]
        except KeyError:
            raise KeyError("Processed image doesn't have ID, it cannot be constructed")
        patient_id = data.get(ProcessedImage.KW_PATIENT_ID, ProcessedImage.V_EMPTY_INT)
        original_image_id = data.get(ProcessedImage.KW_ORIGINAL_IMAGE_ID, ProcessedImage.V_EMPTY_INT)
        used_method_id = data.get(ProcessedImage.KW_USED_METHOD_ID, ProcessedImage.V_EMPTY_INT)
        results = data.get(ProcessedImage.KW_RESULTS, ProcessedImage.V_EMPTY_DICT)
        path_to_image = data.get(ProcessedImage.KW_PATH_TO_IMAGE, ProcessedImage.V_EMPTY_STRING)
        raw_image = data.get(ProcessedImage.KW_RAW_IMAGE, None)
        state = data.get(ProcessedImage.KW_STATE, ProcessedImage.KW_STATE)
        return ProcessedImage(ID, patient_id, original_image_id, used_method_id,
                              results, path_to_image, raw_image, state)

    def deconstructor(self) -> dict:
        """
        Deconstructs ProcessedImage object into dictionary
        :return: (dict) dictionary of processed image data
        """
        deconstructed = {
            ProcessedImage.KW_ID: self.ID,
            ProcessedImage.KW_PATIENT_ID: self.patient_id,
            ProcessedImage.KW_ORIGINAL_IMAGE_ID: self.original_image_id,
            ProcessedImage.KW_USED_METHOD_ID: self.used_method_id,
            ProcessedImage.KW_RESULTS: self.results,
            ProcessedImage.KW_PATH_TO_IMAGE: self.path_to_image,
            ProcessedImage.KW_RAW_IMAGE: self.raw_image,
            ProcessedImage.KW_STATE: self.state
        }

        filtered = {key: value for key, value in deconstructed.items()
                    if value not in [ProcessedImage.V_EMPTY_STRING, ProcessedImage.V_EMPTY_INT, ProcessedImage.V_EMPTY_DICT]
                    }
        return dict(filtered)





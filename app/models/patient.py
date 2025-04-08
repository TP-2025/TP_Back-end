from app.database import Database
from app.services.image_processing_server import IPS


class Patient:
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
            ID = data["id"]
            medic_id = data["lekar_id"]
        except KeyError:
            raise KeyError("Patient doesn't have ID or medic ID, it cannot be constructed")

        name = data.get("meno", "")
        surname = data.get("priezvisko", "")
        year_of_birth = data.get("rok_narodenia", -1)
        sex = data.get("pohlavie", "")
        if safe_mode:
            diagnosis = ""
            medical_notes = ""
        else:
            diagnosis = data.get("diagnoza", "")
            medical_notes = data.get("poznamka_lekara", "")
        return Patient(ID, name, surname, year_of_birth, sex, diagnosis, medical_notes, medic_id, safe_mode)

    def deconstructor(self) -> dict:
        """
        Function for deconstructing Patient object into dict for database use
        :return (dict): dictionary of patient data
        """
        deconstructed = {"id": self.ID,
                         "meno": self.name,
                         "priezvisko": self.surname,
                         "rok_narodenia": self.year_of_birth,
                         "pohlavie": self.sex,
                         "lekar_id": self.medic_id
                         }
        if not self.safe_mode:
            deconstructed = {**deconstructed,
                "diagnoza": self.diagnosis,
                "poznamka_lekara": self.medical_notes,
            }

        return deconstructed

    def add_original_image(self, image, image_data: dict) -> int:
        image_data = {
            "pacient_id": self.ID,
            **image_data,
            "image": image
        }
        db = Database()
        success = db.insert_one_original_image(image_data)
        db.close()
        return success

    def send_image_for_processing(self, method_id: int, image):
        # TODO: needs processing recieved info
        IPS.use_method(method_id, image)

import app.database_oriented.keywords as kw
from app.database_oriented.database import Database
from app.database_oriented.models.modelusers.model_patient import ModelPatient
from app.database_oriented.models.modelusers.model_user import ModelUser


class ModelMedic(ModelUser):
    def __init__(self, ID: int, name: str, surname: str, rights: int, role_id: int, **kwargs):
        super().__init__(ID, name, surname, rights, role_id, **kwargs)

    def get_technics(self):
        # TODO: Needs rework and implementation about storing relation between medic and technics
        # Many to many relation
        return []

    def get_patients(self) -> list[dict]:
        """
        Returns list of patients associated with this medic
        :return: (list[dict]) list of patients
        """
        db = Database()
        if self.rights & kw.ALLOWED_TO_SEE_ALL_PATIENTS:
            found_patients = db.get_patients()
        else:
            found_patients = db.get_patients(medic_id=self.ID)
        db.close()
        return found_patients

    def get_original_images(self) -> list[dict]:
        """
        Returns list of original images associated with this medic
        :return: (list[dict]) list of original images
        """
        found_original_images = []
        db = Database()
        for patient in self.get_patients():
            try:
                patient["safe_mode"] = True
                patient_model = ModelPatient.constructor(patient)
            except TypeError:
                continue
            found_original_images.extend(patient_model.search_original_images("", False))
        db.close()

        return found_original_images

    def get_processed_images(self) -> list[dict]:
        """
        Returns list of processed images associated with this medic
        :return: (list[dict]) list of processed images
        """
        found_processed_images = []
        db = Database()
        for patient in self.get_patients():
            try:
                patient["safe_mode"] = True
                patient_model = ModelPatient.constructor(patient)
            except TypeError:
                continue
            found_processed_images.extend(patient_model.get_processed_images())
        db.close()

        return found_processed_images

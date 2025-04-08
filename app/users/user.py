from app.database import Database
from app.models.patient import Patient


class User:
    # rights
    ALLOWED_TO_ADD_PATIENTS = 1 << 0
    ALLOWED_TO_ADD_MEDICS = 1 << 1
    ALLOWED_TO_ADD_TECHNICS = 1 << 2
    ALLOWED_TO_SEE_ALL_PATIENTS = 1 << 3
    ALLOWED_TO_SEE_ALL_TECHNICS = 1 << 4
    ALLOWED_TO_SEE_ALL_MEDICS = 1 << 5
    ALLOWED_TO_DELETE_PATIENT = 1 << 6
    ALLOWED_TO_DELETE_MEDIC = 1 << 7
    ALLOWED_TO_DELETE_TECHNIC = 1 << 8
    ALLOWED_TO_SEE_MEDICALS = 1 << 9
    ALLOWED_TO_CHANGE_RIGHTS_MEDIC = 1 << 10
    ALLOWED_TO_CHANGE_RIGHTS_TECHNIC = 1 << 11

    ALLOWED_ALL = (1 << 12) - 1

    def __init__(self, ID: int, rights: int, data: dict):
        self.ID = ID
        self.rights = rights
        self.data = data
        self.selected_patient = None

    def search_patients(self, condition: str, medicID: int, simplified: bool = True) -> list:
        db = Database()
        if not(self.rights & User.ALLOWED_TO_SEE_ALL_PATIENTS):
            condition = f"lekar_id = {medicID}" + ("" if condition == "" else " AND ") + condition
        found_patients = db.select_patients(condition)
        db.close()
        if simplified:
            simplified_list = []
            for patient in found_patients:
                try:
                    simplified_list.append({patient["id"], patient["meno"], patient["priezvisko"]})
                except KeyError:
                    continue
            return simplified_list
        else:
            return found_patients

    def select_patient(self, patientID: int) -> [Patient, None]:
        db = Database()
        condition = f"id = {patientID}"
        if not(self.rights & User.ALLOWED_TO_SEE_ALL_PATIENTS):
            condition = f"lekar_id = {self.ID} AND " + condition

        found = db.select_patients(condition)
        db.close()
        try:
            return Patient.constructor(found[0])
        except IndexError:
            return None

    def add_patient(self, data: dict) -> int:
        if self.rights & User.ALLOWED_TO_ADD_PATIENTS:
            db = Database()
            exit_code = db.insert_one_patient(data)
            db.close()
            return exit_code
        else:
            print("Not allowed to add patients")
            return 1

    def delete_patient(self, patient: Patient):
        if self.rights & User.ALLOWED_TO_DELETE_PATIENT:
            condition = f"id = {patient.ID}"
            db = Database()
            exit_code = db.delete_patients(condition)
            # TODO: add deleting images connected to this patient
            db.close()
            return exit_code
        else:
            print("Not allowed to add patients")
            return 1

    # TODO: Add methods for patient changing information
    # TODO: Add methods for technic adding / deleting
    # TODO: Add methods for medic adding / deleting



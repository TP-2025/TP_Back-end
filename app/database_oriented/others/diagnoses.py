from app.database_oriented.database import Database
import app.database_oriented.keywords as kw
from app.database_oriented.exitcodes_errors import ExitCodes


class Diagnose:
    def __init__(self, diagnose_id, diagnose_name):
        self.diagnose_id = diagnose_id
        self.diagnose_name = diagnose_name

    @staticmethod
    def get_diagnose_by_id(diagnose_id: int) -> dict:
        db = Database()
        try:
            diagnose = db.select_diagnoses(f"{kw.KW_DIAGNOSIS_ID} = {diagnose_id}")[0]
            db.close()
        except IndexError:
            db.close()
            raise IndexError(f"Diagnose with given ID '{diagnose_id}' not found")
        return diagnose

    @staticmethod
    def get_diagnose_by_name(diagnose_name: str) -> dict:
        db = Database()
        try:
            diagnose = db.select_diagnoses(f"{kw.KW_DIAGNOSIS_NAME} = '{diagnose_name}'")[0]
            db.close()
        except IndexError:
            db.close()
            raise IndexError(f"Diagnose with given name '{diagnose_name}' not found")
        return diagnose

    @staticmethod
    def get_all_diagnoses() -> list:
        db = Database()
        diagnoses = db.select_diagnoses()
        db.close()
        return diagnoses

    @staticmethod
    def add_diagnose(diagnose_name: str) -> int:
        db = Database()
        diagnose_id = db.insert_one_diagnosis({kw.KW_DIAGNOSIS_NAME: diagnose_name})
        db.close()
        return diagnose_id

    @staticmethod
    def delete_diagnose_by_id(diagnose_id: int) -> int:
        db = Database()
        exit_code = db.delete_diagnoses(f"{kw.KW_DIAGNOSIS_ID} = {diagnose_id}")
        db.close()
        return exit_code

    @staticmethod
    def delete_multiple_diagnoses(diagnose_ids: list) -> int:
        db = Database()
        exit_code = ExitCodes.SUCCESS
        for diagnose_id in diagnose_ids:
            exit_code |= db.delete_diagnoses(f"{kw.KW_DIAGNOSIS_ID} = {diagnose_id}")
        db.close()
        return exit_code

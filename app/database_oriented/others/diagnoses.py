from app.database_oriented.database import Database
import app.database_oriented.keywords as kw
from app.database_oriented.exitcodes_errors import ExitCodes


class Diagnose:
    def __init__(self, diagnose_id, diagnose_name):
        self.diagnose_id = diagnose_id
        self.diagnose_name = diagnose_name

    @staticmethod
    def get_diagnose_by_id(diagnose_id: int) -> dict:
        """
        Returns diagnose with a given ID
        :param diagnose_id: (int) diagnose ID
        :return: (dict) diagnose
        :raise IndexError: if diagnose with given ID not found
        """
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
        """
        Returns diagnose with a given name
        :param diagnose_name: (str) diagnose name
        :return: (dict) diagnose
        :raise IndexError: if diagnose with given name not found
        """
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
        """
        Returns all diagnoses
        :return: (list) list of diagnoses
        """
        db = Database()
        diagnoses = db.select_diagnoses()
        db.close()
        return diagnoses

    @staticmethod
    def add_diagnose(diagnose_name: str) -> int:
        """
        Adds diagnose to the database
        :param diagnose_name: (str) diagnose name
        :return: (int) exit code
        """
        db = Database()
        exit_code = db.insert_one_diagnosis({kw.KW_DIAGNOSIS_NAME: diagnose_name})
        db.close()
        return exit_code

    @staticmethod
    def delete_diagnose_by_id(diagnose_id: int) -> int:
        """
        Deletes diagnose by ID
        :param diagnose_id: (int) diagnose ID
        :return: (int) exit code
        """
        db = Database()
        exit_code = db.delete_diagnoses(f"{kw.KW_DIAGNOSIS_ID} = {diagnose_id}")
        db.close()
        return exit_code

    @staticmethod
    def delete_multiple_diagnoses_by_ids(diagnose_ids: list[int]) -> int:
        """
        Deletes multiple diagnoses
        :param diagnose_ids: (list[int]) list of diagnose IDs
        :return: (int) exit code
        """
        db = Database()
        exit_code = ExitCodes.SUCCESS
        for diagnose_id in diagnose_ids:
            exit_code |= db.delete_diagnoses(f"{kw.KW_DIAGNOSIS_ID} = {diagnose_id}")
        db.close()
        return exit_code

    @staticmethod
    def delete_diagnose_by_names(diagnose_names: list[str]) -> int:
        """
        Deletes diagnose by name
        :param diagnose_names: (list[str]) list of diagnose names
        :return: (int) exit code
        """
        db = Database()
        exit_code = ExitCodes.SUCCESS
        for diagnose_name in diagnose_names:
            exit_code |= db.delete_diagnoses(f"{kw.KW_DIAGNOSIS_NAME} = '{diagnose_name}'")
        db.close()
        return exit_code

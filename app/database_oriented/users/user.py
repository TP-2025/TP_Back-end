from app.database_oriented.database import Database
from app.database_oriented.models.patient import Patient as PatientModel
from app.database_oriented.models.user import User as UserModel


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
    ALLOWED_TO_CHANGE_ROLES = 1 << 12

    ALLOWED_ALL = (1 << 13) - 1

    def __init__(self, ID: int, rights: int, data: dict):
        self.ID = ID
        self.rights = rights
        self.data = data
        self.selected_patient = None
        self.selected_original_image = None
        self.selected_processed_image = None

    def get_rights(self) -> dict:
        """
        Returns dictionary of user rights
        :return:
        """
        return {
            "add_patients": bool(self.rights & User.ALLOWED_TO_ADD_PATIENTS),
            "add_medics": bool(self.rights & User.ALLOWED_TO_ADD_MEDICS),
            "add_technics": bool(self.rights & User.ALLOWED_TO_ADD_TECHNICS),
            "see_all_patients": bool(self.rights & User.ALLOWED_TO_SEE_ALL_PATIENTS),
            "see_all_technics": bool(self.rights & User.ALLOWED_TO_SEE_ALL_TECHNICS),
            "see_all_medics": bool(self.rights & User.ALLOWED_TO_SEE_ALL_MEDICS),
            "delete_patient": bool(self.rights & User.ALLOWED_TO_DELETE_PATIENT),
            "delete_medic": bool(self.rights & User.ALLOWED_TO_DELETE_MEDIC),
            "delete_technic": bool(self.rights & User.ALLOWED_TO_DELETE_TECHNIC),
            "see_medicals": bool(self.rights & User.ALLOWED_TO_SEE_MEDICALS),
            "change_rights_medic": bool(self.rights & User.ALLOWED_TO_CHANGE_RIGHTS_MEDIC),
            "change_rights_technic": bool(self.rights & User.ALLOWED_TO_CHANGE_RIGHTS_TECHNIC),
            "change_roles": bool(self.rights & User.ALLOWED_TO_CHANGE_ROLES)
        }

    def is_change_of_rights_allowed(self, user: UserModel, rights: int) -> bool:
        """
        Function checks if user is allowed to change rights
        :param user: (app.models.user.User)
        :param rights:
        :return:
        """
        changed_bits = rights ^ user.rights
        if user.role == "lekar":
            needed_bits = changed_bits | User.ALLOWED_TO_CHANGE_RIGHTS_MEDIC
        elif user.role == "technik":
            needed_bits = changed_bits | User.ALLOWED_TO_CHANGE_RIGHTS_TECHNIC
        else:
            return False
        return (needed_bits & self.rights) == needed_bits

    def update_rights(self, allow_rights: int, deny_rights: int, userID: int):
        db = Database()
        try:
            user = db.select_users(f"id = {userID}")[0]
        except IndexError:
            raise IndexError("User not found")

        user = UserModel.constructor(user)
        rights = (user.rights | allow_rights) & (~deny_rights)
        allowed = self.is_change_of_rights_allowed(user, rights)
        if allowed:
            user.update_rights(rights)
            exit_code = db.update_users({"prava": rights}, f"id = {userID}")
            db.close()
            return exit_code
        else:
            db.close()
            raise PermissionError("Not allowed to change rights")

    def change_rights(self, rights: int, userID: int):
        db = Database()
        try:
            user = db.select_users(f"id = {userID}")[0]
        except IndexError:
            raise IndexError("User not found")

        user = UserModel.constructor(user)
        allowed = self.is_change_of_rights_allowed(user, rights)

        if allowed:
            user.update_rights(rights)
            exit_code = db.update_users({"prava": rights}, f"id = {userID}")
            db.close()
            return exit_code
        else:
            db.close()
            raise PermissionError("Not allowed to change rights")

    def search_patients(self, condition: str, medicID: int, simplified: bool = True) -> list:
        """
        Searches in database for patients using SQL WHERE condition
        :param condition: (str) SQL WHERE condition
        :param medicID: (int) ID of medic to filter the patients.
            If -1, no filtering (usable with ALLOWED_TO_SEE_ALL_PATIENTS)
        :param simplified: (bool) if True, returns simplified list
        :return: (list) list of patients
        """
        db = Database()
        if not (self.rights & User.ALLOWED_TO_SEE_ALL_PATIENTS):
            condition = f"lekar_id = {medicID}" + ("" if condition == "" else " AND ") + condition
        found_patients = db.select_patients(condition)
        db.close()
        if simplified:
            simplified_list = []
            for patient in found_patients:
                try:
                    simplified_list.append({
                        "id": patient["id"],
                        "name": patient["meno"],
                        "surname": patient["priezvisko"]
                    })
                except KeyError:
                    continue
            return simplified_list
        else:
            return found_patients

    def select_patient(self, patientID: int, safe_mode: bool = False) -> [PatientModel, None]:
        """
        Selects patient with a given ID from database
        :param patientID:
        :return: [Patient, None] returns selected Patient object or None
        """
        db = Database()
        condition = f"id = {patientID}"
        if not (self.rights & User.ALLOWED_TO_SEE_ALL_PATIENTS):
            condition = f"lekar_id = {self.ID} AND " + condition

        found = db.select_patients(condition)
        db.close()
        try:
            return PatientModel.constructor(found[0], safe_mode)
        except IndexError:
            return None

    def add_patient(self, data: dict) -> int:
        """
        Adds patient to the database. Needs to have right to add patients
        :param data:
        :return:
        """
        if self.rights & User.ALLOWED_TO_ADD_PATIENTS:
            db = Database()
            exit_code = db.insert_one_patient(data)
            db.close()
            return exit_code
        else:
            print("Not allowed to add patients")
            return 1

    def delete_patient(self, patient: PatientModel):
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

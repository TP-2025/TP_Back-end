import app.database_oriented.keywords as kw
from app.database_oriented.database import Database


class ModelUser:
    def __init__(self, ID: int, name: str, surname: str, rights: int, role_id: int, **kwargs):
        self.ID = ID
        self.rights = rights
        self.role_id = role_id
        self.role_name = Database.get_role_by_id(role_id)
        self.name = name
        self.surname = surname

        self.email = kwargs.get(kw.KW_USER_EMAIL, kw.V_EMPTY_STRING)
        self.sex = kwargs.get(kw.KW_USER_SEX, kw.V_EMPTY_STRING)
        self.date_of_birth = kwargs.get(kw.KW_USER_DATE_OF_BIRTH, kw.V_EMPTY_INT)

        self.data = kwargs
        self.selected_image = None

    @classmethod
    def constructor(cls, data: dict):
        """Constructs ModelUser object from raw data from database

        :param data: (dict) user data from database
        :return: (ModelUser) new ModelUser object from raw data
        """
        try:
            ID = data.pop(kw.KW_USER_ID, -2222)
            role_id = data.pop(kw.KW_USER_ROLE_ID, -2222)
            if -2222 in [ID, role_id]:
                raise KeyError
        except KeyError:
            raise KeyError("ModelUser doesn't have ID or role_id, it cannot be constructed")
        rights = data.pop(kw.KW_USER_RIGHTS, 0)
        name = data.pop(kw.KW_USER_NAME, kw.V_EMPTY_STRING)
        surname = data.pop(kw.KW_USER_SURNAME, kw.V_EMPTY_STRING)

        return cls(ID, name, surname, rights, role_id, **data)

    def deconstructor(self):
        """Deconstructs ModelUser object to dictionary of its attributes

        :return: (dict) dictionary of user data
        """
        deconstructed = {**self.data,
                         kw.KW_USER_ID: self.ID,
                         kw.KW_USER_EMAIL: self.email,
                         kw.KW_USER_RIGHTS: self.rights,
                         kw.KW_USER_ROLE_ID: self.role_id,
                         kw.KW_USER_NAME: self.name,
                         kw.KW_USER_SURNAME: self.surname,
                         kw.KW_ROLE_NAME: self.role_name,
                         kw.KW_USER_DATE_OF_BIRTH: self.date_of_birth,
                         kw.KW_USER_SEX: self.sex
                         }
        filtered = {key: value for key, value in deconstructed.items()
                    if value not in [kw.V_EMPTY_STRING, kw.V_EMPTY_INT, kw.V_EMPTY_DICT]
                    }
        return dict(filtered)

    @staticmethod
    def get_user_by_id(user_id: int) -> ["ModelUser", None]:
        """Selects user with a given ID from database

        :param user_id: (int) ID of user
        :return: (ModelUser) user object or None if user not found
        """
        db = Database()
        user = db.get_users(user_id)
        db.close()

        try:
            return ModelUser.constructor(user[0])
        except IndexError:
            return None

    def _update_rights(self, rights: int):
        """Updates rights of user in database

        :param rights: (int) new rights of user in database"""
        self.rights = rights

    def delete_me(self) -> int:
        """Deletes user from database
        :return: (int) exit code
        """
        db = Database()
        exit_code = db.delete_users(f"{kw.KW_USER_ID} = {self.ID}")
        exit_code |= db.close()
        return exit_code

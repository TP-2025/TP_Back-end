
class ModelUser:
    # Keywords for accessing users in database
    KW_ID = "id"
    KW_ROLE = "role"
    KW_FULL_NAME = "meno"
    KW_RIGHTS = "prava"
    KW_EMAIL = "email"
    KW_HASHED_PASSWORD = "heslo"

    # Default values of empty data
    V_EMPTY_STRING = "Nothing here"
    V_EMPTY_INT = -1111
    V_EMPTY_DICT = {"empty": "empty"}

    def __init__(self, ID: int, rights: int, role: str, full_name: str):
        self.ID = ID
        self.rights = rights
        self.role = role
        self.full_name = full_name

    @staticmethod
    def constructor(data: dict):
        """Constructs ModelUser object from raw data from database

        :param data: (dict) user data from database
        :return: (ModelUser) new ModelUser object from raw data
        """
        try:
            ID = data[ModelUser.KW_ID]
        except KeyError:
            raise KeyError("ModelUser doesn't have ID, it cannot be constructed")
        rights = data.get(ModelUser.KW_RIGHTS, 0)
        role = data.get(ModelUser.KW_ROLE, ModelUser.V_EMPTY_STRING)
        full_name = data.get(ModelUser.KW_FULL_NAME, ModelUser.V_EMPTY_STRING)
        return ModelUser(ID, rights, role, full_name)

    def deconstructor(self):
        """Deconstructs ModelUser object to dictionary of its attributes

        :return: (dict) dictionary of user data
        """
        deconstructed = {
            ModelUser.KW_ID: self.ID,
            ModelUser.KW_RIGHTS: self.rights,
            ModelUser.KW_ROLE: self.role,
            ModelUser.KW_FULL_NAME: self.full_name
        }
        filtered = {key: value for key, value in deconstructed.items()
                    if value not in [ModelUser.V_EMPTY_STRING, ModelUser.V_EMPTY_INT, ModelUser.V_EMPTY_DICT]
                    }
        return dict(filtered)

    def update_rights(self, rights: int):
        """Updates rights of user in database

        :param rights: (int) new rights of user in database"""
        self.rights = rights



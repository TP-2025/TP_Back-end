
class User:
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
        """Constructs User object from raw data from database

        :param data: (dict) user data from database
        :return: (User) new User object from raw data
        """
        try:
            ID = data[User.KW_ID]
        except KeyError:
            raise KeyError("User doesn't have ID, it cannot be constructed")
        rights = data.get(User.KW_RIGHTS, 0)
        role = data.get(User.KW_ROLE, User.V_EMPTY_STRING)
        full_name = data.get(User.KW_FULL_NAME, User.V_EMPTY_STRING)
        return User(ID, rights, role, full_name)

    def deconstructor(self):
        """Deconstructs User object to dictionary of its attributes

        :return: (dict) dictionary of user data
        """
        deconstructed = {
            User.KW_ID: self.ID,
            User.KW_RIGHTS: self.rights,
            User.KW_ROLE: self.role,
            User.KW_FULL_NAME: self.full_name
        }
        filtered = {key: value for key, value in deconstructed.items()
                    if value not in [User.V_EMPTY_STRING, User.V_EMPTY_INT, User.V_EMPTY_DICT]
                    }
        return dict(filtered)

    def update_rights(self, rights: int):
        """Updates rights of user in database

        :param rights: (int) new rights of user in database"""
        self.rights = rights



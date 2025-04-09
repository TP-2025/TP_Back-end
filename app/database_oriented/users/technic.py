from app.database_oriented.database import Database
from app.database_oriented.models.model_user import ModelUser
from app.database_oriented.users.user import User


class Technic(User):
    def __init__(self, ID: int, rights: int, full_name: str):
        super().__init__(ID, rights, User.ROLE_TECHNIC, full_name)

    @staticmethod
    def get_technic(ID: int) -> "Technic":
        db = Database()
        found = db.select_users(f"{ModelUser.KW_ID} = {ID}")
        try:
            user = ModelUser.constructor(found[0])
            assert user.role == User.ROLE_TECHNIC, f"User with given ID {ID} is not {User.ROLE_TECHNIC}"
            db.close()
        except IndexError:
            db.close()
            raise IndexError(f"User with given ID '{ID}' not found")
        except AssertionError as e:
            db.close()
            raise AssertionError(e)

        return Technic(ID, user.rights, user.full_name)

from app.database_oriented.database import Database
from app.database_oriented.models.model_user import ModelUser
from app.database_oriented.users.user import User


class Admin(User):
    def __init__(self, ID: int, rights: int, full_name: str):
        super().__init__(ID, rights, User.ROLE_ADMIN, full_name)

    @staticmethod
    def get_admin(ID: int) -> "Admin":
        db = Database()
        found = db.select_users(f"{ModelUser.KW_ID} = {ID}")
        try:
            user = ModelUser.constructor(found[0])
            assert user.role == User.ROLE_ADMIN, f"User with given ID {ID} is not {User.ROLE_ADMIN}"
            db.close()
        except IndexError:
            db.close()
            raise IndexError(f"User with given ID '{ID}' not found")
        except AssertionError as e:
            db.close()
            raise AssertionError(e)

        return Admin(ID, user.rights, user.full_name)

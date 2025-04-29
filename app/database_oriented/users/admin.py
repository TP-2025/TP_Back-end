from app.database_oriented.database import Database
from app.database_oriented.models.model_user import ModelUser
from app.database_oriented.users.user import User


class Admin(User):
    def __init__(self, ID: int, full_name: str):
        super().__init__(ID, User.ALLOWED_ALL, User.ROLE_ADMIN, full_name)

    @staticmethod
    def get_admin(ID: int) -> "Admin":
        db = Database()
        found = db.select_users(f"{ModelUser.KW_ID} = {ID}")
        db.close()
        try:
            user = ModelUser.constructor(found[0])
            assert user.role == User.ROLE_ADMIN, f"User with given ID {ID} is not {User.ROLE_ADMIN}"
        except IndexError:
            raise IndexError(f"User with given ID '{ID}' not found")
        except AssertionError as e:
            raise AssertionError(e)

        return Admin(ID, user.full_name)

    def is_allowed_to_add_users(self, target_role: str) -> bool:
        """
        Checks if user is allowed to add users of given role (admin can add any user)
        :param target_role: (str) role of user (lekar, technik, pacient)
        :return: (bool) True if user is allowed to add users of given role
        :return:
        """
        return True

    def is_change_of_rights_allowed(self, user: ModelUser, rights: int) -> bool:
        """
        Function checks if user is allowed to change rights
        :param user: (app.models.user.User)
        :param rights:
        :return: (bool) True, admin can change rights
        """
        return True

from app.database_oriented.database import Database
import app.database_oriented.keywords as kw


class Method:
    def __init__(self, ID: int, method: str):
        self.ID = ID
        self.method = method

    @staticmethod
    def get_method_by_id(method_id: int) -> dict:
        """
        Retrieves a method from the kw.TBL_METHODS table based on its ID.

        :param method_id: (int): ID of the method to retrieve.
        :return: (dict) method
        :raise: IndexError if method with given ID not found
        """
        db = Database()
        try:
            method = db.select_methods(f"{kw.KW_METHOD_ID} = {method_id}")[0]
            db.close()
        except IndexError:
            db.close()
            raise IndexError(f"Method with given ID '{method_id}' not found")

        return method

    @staticmethod
    def get_method_by_name(method_name: str) -> dict:
        """
        Retrieves a method from the kw.TBL_METHODS table based on its name.

        :param method_name: (str): Name of the method to retrieve.
        :return: (dict) method
        :raise: IndexError if method with given name not found
        """
        db = Database()
        try:
            method = db.select_methods(f"{kw.KW_METHOD_NAME} = '{method_name}'")[0]
            db.close()
        except IndexError:
            db.close()
            raise IndexError(f"Method with given name '{method_name}' not found")

        return method

    @staticmethod
    def add_method(data: dict) -> int:
        """
        Adds a method to the kw.TBL_METHODS table.

        :param data: (dict): Dictionary containing method fields.
        :return: (int) ExitCodes.SUCCESS on success, ExitCodes.DATABASE_INSERT_ERROR on error.
        """
        db = Database()
        exit_code = db.insert_one_method(data)
        db.close()
        return exit_code

    @staticmethod
    def delete_method_by_id(method_id: int) -> int:
        """
        Deletes a method from the kw.TBL_METHODS table based on its ID.

        :param method_id: (int): ID of the method to delete.
        :return: (int) ExitCodes.SUCCESS on success, ExitCodes.DATABASE_DELETE_ERROR on error.
        """
        db = Database()
        exit_code = db.delete_methods(f"{kw.KW_METHOD_ID} = {method_id}")
        db.close()
        return exit_code

    @staticmethod
    def delete_method_by_name(method_name: str) -> int:
        """
        Deletes a method from the kw.TBL_METHODS table based on its name.

        :param method_name: (str): Name of the method to delete.
        :return: (int) ExitCodes.SUCCESS on success, ExitCodes.DATABASE_DELETE_ERROR on error.
        """
        db = Database()
        exit_code = db.delete_methods(f"{kw.KW_METHOD_NAME} = '{method_name}'")
        db.close()
        return exit_code

    @staticmethod
    def update_method_by_id(method_id: int, data: dict) -> int:
        """
        Updates a method in the kw.TBL_METHODS table based on its ID.

        :param method_id: (int): ID of the method to update.
        :param data: (dict): Dictionary containing updated method fields.
        :return: (int) ExitCodes.SUCCESS on success, ExitCodes.DATABASE_UPDATE_ERROR on error.
        """
        db = Database()
        exit_code = db.update_methods(data, f"{kw.KW_METHOD_ID} = {method_id}")
        db.close()
        return exit_code

    @staticmethod
    def get_all_methods() -> list:
        """
        Retrieves all methods from the kw.TBL_METHODS table.

        :return: (list) List of methods.
        """
        db = Database()
        methods = db.select_methods("")
        db.close()
        return methods




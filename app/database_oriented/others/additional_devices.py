from app.database_oriented.database import Database
import app.database_oriented.keywords as kw


class AdditionalDevices:
    def __init__(self, ID: int, name: str):
        self.ID = ID
        self.name = name

    @staticmethod
    def get_additional_device_by_id(ID: int) -> dict:
        """
        Returns additional device with a given ID
        :param ID: (int) additional device ID
        :return: (dict) additional device
        :raise: IndexError: if additional device with given ID not found
        """
        db = Database()
        try:
            additional_device = db.select_additional_devices(f"{kw.KW_ADD_DEVICE_ID} = {ID}")[0]
            db.close()
        except IndexError:
            db.close()
            raise IndexError(f"Additional device with given ID '{ID}' not found")
        return additional_device

    @staticmethod
    def get_additional_device_by_name(name: str) -> dict:
        """
        Returns additional device with a given name
        :param name: (str) additional device name
        :return: (dict) additional device
        :raise: IndexError: if additional device with given name not found
        """
        db = Database()
        try:
            additional_device = db.select_additional_devices(f"{kw.KW_ADD_DEVICE_NAME} = '{name}'")[0]
            db.close()
        except IndexError:
            db.close()
            raise IndexError(f"Additional device with given name '{name}' not found")
        return additional_device

    @staticmethod
    def add_additional_device(data: dict) -> int:
        """
        Adds additional device to the database
        :param data: (dict) dictionary of additional device data
        :return: (int) exit code
        """
        db = Database()
        exit_code = db.insert_one_additional_device(data)
        db.close()
        return exit_code

    @staticmethod
    def delete_additional_device_by_id(ID: int) -> int:
        """
        Deletes additional device by ID
        :param ID: (int) additional device ID
        :return: (int) exit code
        """
        db = Database()
        exit_code = db.delete_additional_devices(f"{kw.KW_ADD_DEVICE_ID} = {ID}")
        db.close()
        return exit_code

    @staticmethod
    def update_additional_device_by_id(ID: int, data: dict) -> int:
        """
        Updates additional device by ID
        :param ID: (int) additional device ID
        :param data: (dict) dictionary of additional device data
        :return: (int) exit code
        """
        db = Database()
        exit_code = db.update_additional_devices(data, f"{kw.KW_ADD_DEVICE_ID} = {ID}")
        db.close()
        return exit_code

    @staticmethod
    def get_all_additional_devices() -> list[dict]:
        """
        Returns all additional devices
        :return: (list[dict]) list of additional devices
        """
        db = Database()
        additional_devices = db.select_additional_devices("")
        db.close()
        return additional_devices

from app.database_oriented.database import Database
import app.database_oriented.keywords as kw


class Device:
    def __init__(self, ID: int, name: str, type: str):
        self.ID = ID
        self.name = name
        self.type = type

    @staticmethod
    def get_device_by_id(ID: int) -> dict:
        """
        Returns device with a given ID
        :param ID: (int) device ID
        :return: (dict) device
        :raise: IndexError: if device with given ID not found
        """
        db = Database()
        try:
            device = db.select_devices(f"{kw.KW_DEVICE_ID} = {ID}")[0]
            db.close()
        except IndexError:
            db.close()
            raise IndexError(f"Device with given ID '{ID}' not found")
        return device

    @staticmethod
    def get_device_by_name(name: str) -> dict:
        """
        Returns device with a given name
        :param name: (str) device name
        :return: (dict) device
        :raise: IndexError: if device with given name not found
        """
        db = Database()
        try:
            device = db.select_devices(f"{kw.KW_DEVICE_NAME} = '{name}'")[0]
            db.close()
        except IndexError:
            db.close()
            raise IndexError(f"Device with given name '{name}' not found")
        return device

    @staticmethod
    def add_device(data: dict) -> int:
        """
        Adds device to the database
        :param data: (dict) dictionary of device data
        :return: (int) exit code
        """
        db = Database()
        exit_code = db.insert_one_device(data)
        db.close()
        return exit_code

    @staticmethod
    def delete_device_by_id(ID: int) -> int:
        """
        Deletes device by ID
        :param ID: (int) device ID
        :return: (int) exit code
        """
        db = Database()
        exit_code = db.delete_devices(f"{kw.KW_DEVICE_ID} = {ID}")
        db.close()
        return exit_code

    @staticmethod
    def update_device_by_id(ID: int, data: dict) -> int:
        """
        Updates device by ID
        :param ID: (int) device ID
        :param data: (dict) dictionary of device data
        :return: (int) exit code
        """
        db = Database()
        exit_code = db.update_devices(data, f"{kw.KW_DEVICE_ID} = {ID}")
        db.close()
        return exit_code

    @staticmethod
    def get_all_devices() -> list[dict]:
        """
        Returns all devices
        :return: (list[dict]) list of devices
        """
        db = Database()
        devices = db.select_devices("")
        db.close()
        return devices

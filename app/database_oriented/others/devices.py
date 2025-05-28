from app.database_oriented.database import Database
import app.database_oriented.keywords as kw


class Device:
    def __init__(self, ID: int, name: str, type: str):
        self.ID = ID
        self.name = name
        self.type = type

    @staticmethod
    def get_device_by_id(ID: int) -> dict:
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
        db = Database()
        exit_code = db.insert_one_device(data)
        db.close()
        return exit_code

    @staticmethod
    def delete_device_by_id(ID: int) -> int:
        db = Database()
        exit_code = db.delete_devices(f"{kw.KW_DEVICE_ID} = {ID}")
        db.close()
        return exit_code

    @staticmethod
    def get_all_devices() -> list[dict]:
        db = Database()
        devices = db.select_devices("")
        db.close()
        return devices

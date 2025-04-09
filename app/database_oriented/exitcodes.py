class ExitCodes:
    SUCCESS = 0
    PERMISSION_DENIED = 1 << 0
    OPERATION_FAILED = 1 << 1
    INVALID_SOURCE_ROLE = 1 << 2
    INVALID_TARGET_ROLE = 1 << 3
    USER_NOT_FOUND = 1 << 4
    DATABASE_INSERT_ERROR = 1 << 5
    DATABASE_DELETE_ERROR = 1 << 6
    DATABASE_SELECT_ERROR = 1 << 7
    DATABASE_UPDATE_ERROR = 1 << 8

    error_code = 0

    @classmethod
    def clear_error_code(cls, code: int):
        cls.error_code = code

    @classmethod
    def error_words(cls, code: int) -> str:
        error_message = ""
        if code == 0:
            return "No errors\n"
        if code & cls.PERMISSION_DENIED:
            error_message += "Permission denied\n"
        if code & cls.OPERATION_FAILED:
            error_message += "Operation failed\n"
        if code & cls.INVALID_SOURCE_ROLE:
            error_message += "Invalid source role\n"
        if code & cls.INVALID_TARGET_ROLE:
            error_message += "Invalid target role\n"
        if code & cls.USER_NOT_FOUND:
            error_message += "User not found\n"
        if code & cls.DATABASE_INSERT_ERROR:
            error_message += "Database insert error\n"
        if code & cls.DATABASE_DELETE_ERROR:
            error_message += "Database delete error\n"
        if code & cls.DATABASE_SELECT_ERROR:
            error_message += "Database select error\n"
        if code & cls.DATABASE_UPDATE_ERROR:
            error_message += "Database update error\n"
        return error_message

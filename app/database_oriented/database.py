import mysql.connector
import app.database_oriented.keywords as kw

from app.database_oriented.exitcodes_errors import ExitCodes

"""
Uses:
 - db_is_ready: bool = database_object.is_ready()
 - success: int = database_object.insert_one_[user, patient, original_image, processed_image, device](data: dict)
 - success: int = database_object.insert_[users, patients, original_images, processed_images, devices](data: list[dict, ])
 - success: int = database_object.delete_[users, patients, original_images, processed_images, devices](SQL_condition: str)
 - found: list = database_object.select_[users, patients, original_images, processed_images, devices](SQL_condition: str)
 - count: int = database_object.count_[users, patients, original_images, processed_images, devices](SQL_condition: str)
 
For example:
 - success = database_object.insert_one_patient({'meno': 'Mike', 'priezvisko': 'Wazowski', 'datum_narodenia': '2001-01-02', 'lekar_id': 1})
 - success = database_object.insert_users([
       {'meno': 'Hero Brain', 'email': 'hero.brain@example.com', 'heslo_hash': 'hashedpassword123', 'rola': 'Lekár'},
       {'meno': 'James Bond', 'email': 'bond.jamesbond@gama.com', 'heslo_hash': 'hashedpassword456', 'rola': 'Technik'}
   ])
 - success = database_object.delete_devices("id = 2")
 - found_patients = database_object.select_patients("meno = 'Mike' AND priezvisko = 'Wazowski'")
"""


class Database:
    def __init__(self):
        """
        Initializes the database connection object.

        Attempts to connect to the MySQL database and create a cursor.

        Attributes:
            self.conn: Holds the connection object if successful, otherwise None.
            self.cursor: Holds the cursor object if successful, otherwise None.

        :raise
        - ConnectionError: If the connection to the database fails.
        - Exception: For any other unexpected errors during setup.
        """

        # defining/creating connection with database
        self.conn = None
        self.cursor = None
        db_config = {
            # data for database connection (for now for test -> need to change)
            "host": "sql7.freesqldatabase.com",
            "user": "sql7774696",
            "password": "A3NhQWp1Iu",
            "database": "sql7774696",
            "port": 3306
        }

        try:
            # Attempt to establish the connection
            self.conn = mysql.connector.connect(**db_config)

            # Check if the connection was successful before creating cursor
            if self.conn.is_connected():
                # defining cursor for interaction with database
                self.cursor = self.conn.cursor(dictionary=True)
                if self.cursor is None:
                    raise ConnectionError("Failed to create cursor")
            else:
                raise ConnectionError("Connection to database failed validation check")

        except mysql.connector.Error as err:
            raise ConnectionError(f"Error connecting to MySQL database: \n"
                                  f"Error Code: {err.errno}\n"
                                  f"SQLSTATE: {err.sqlstate}\n"
                                  f"Message: {err.msg}")

        except Exception as e:
            # Catch any other unexpected errors during setup
            print(f"An unexpected error occurred during database initialization: {e}")
            if self.conn and self.conn.is_connected():
                self.conn.close()  # Attempt to close connection if it was partially established
            self.conn = None
            self.cursor = None
            raise e

    @staticmethod
    def _filter_dict(data: dict, allowed_keys: list) -> dict:
        """Filters a dictionary to include only the specified keys.
        :parameter
         - data (dict): The dictionary to filter.
         - allowed_keys (list): The list of allowed keys from kw library.
        :return filtered_dict (dict): The filtered dictionary.
        """
        return {key: value for key, value in data.items() if key in allowed_keys}

    def is_ready(self) -> bool:
        """Checks if the database connection and cursor are ready.

        :return is_ready (bool)
        """
        return (self.conn is not None and self.conn.is_connected()) and self.cursor is not None

    # Function for inserting data to table (it is not meant to be accessed directly)
    def __insert(self, table: str, data: list) -> int:
        """
        Inserts one or multiple records into a specified table.

        Parameters:
        - table (str): The name of the table to insert data into.
        - data (list): A list of dictionaries, where each dictionary represents a row to insert.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_INSERT_ERROR on error.
        """
        try:
            placeholders = ', '.join(['%s'] * len(data[0]))
            columns = ', '.join(data[0].keys())
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            values = [tuple(d.values()) for d in data]
            self.cursor.executemany(sql, values)
            self.conn.commit()
            return ExitCodes.SUCCESS
        except mysql.connector.Error as err:
            print(f"[INSERT ERROR] {err}")
            self.close()
            return ExitCodes.DATABASE_INSERT_ERROR
        except IndexError as err:
            print(f"[INSERT ERROR] {err}")
            self.close()
            return ExitCodes.DATABASE_INSERT_ERROR | ExitCodes.INDEX_ERROR

    def __delete(self, table: str, condition: str) -> int:
        """
        Deletes records from a specified table based on a condition.

        Parameters:
        - table (str): The name of the table to delete from.
        - condition (str): SQL condition for selecting rows to delete.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_DELETE_ERROR on error.
        """
        try:
            sql = f"DELETE FROM {table} WHERE {condition}"
            self.cursor.execute(sql)
            self.conn.commit()
            return 0
        except mysql.connector.Error as err:
            print(f"[DELETE ERROR] {err}")
            self.close()
            return ExitCodes.DATABASE_DELETE_ERROR

    def __select(self, table: str, condition: str = None) -> list:
        """
        Selects and returns rows from a specified table.

        Parameters:
        - table (str): The name of the table to select from.
        - condition (str, optional): SQL WHERE condition for filtering rows.

        Returns:
        - list: A list of dictionaries containing the result rows, or empty list on error.
        """
        try:
            sql = f"SELECT * FROM {table}"
            if condition:
                sql += f" WHERE {condition}"
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"[SELECT ERROR] {err}")
            self.close()
            return []

    def __count(self, table: str, condition: str = None) -> int:
        """
        Counts rows in a specified table.

        Parameters:
        - table (str): The name of the table to count rows from.
        - condition (str, optional): SQL WHERE condition to filter which rows to count.

        Returns:
        - int: The number of rows matching the condition, or -1 on error.
        """
        try:
            sql = f"SELECT COUNT(*) AS count FROM {table}"
            if condition:
                sql += f" WHERE {condition}"
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            return result['count'] if result else 0
        except mysql.connector.Error as err:
            print(f"[COUNT ERROR] {err}")
            self.close()
            return -1

    def __update(self, table: str, updates: dict, condition: str) -> int:
        """
        Updates specific columns in a table based on a condition.

        Parameters:
        - table (str): The table name to update.
        - updates (dict): Dictionary of column-value pairs to update.
        - condition (str): SQL WHERE condition to specify which rows to update.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_UPDATE_ERROR on error.
        """
        try:
            set_clause = ', '.join([f"{col} = %s" for col in updates.keys()])
            sql = f"UPDATE {table} SET {set_clause} WHERE {condition}"
            self.cursor.execute(sql, list(updates.values()))
            self.conn.commit()
            return 0
        except mysql.connector.Error as err:
            print(f"[UPDATE ERROR] {err}")
            self.close()
            return ExitCodes.DATABASE_UPDATE_ERROR

    def close(self) -> int:
        """
        Closes the database connection and cursor.

        Returns:
        - int: 0 when successfully closed.
        """
        self.cursor.close()
        self.conn.close()
        return 0

    # Users
    def get_users(self, user_id: int = kw.V_NULL) -> list:
        """
        Database call returning merged tables for users and roles
        :param user_id: (int, optional) ID of user to get, keep empty to get all users
        :return: (list) list of found users
        """
        try:
            sql = f"CALL get_user(%s)"
            self.cursor.execute(sql, (user_id,))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"[SELECT ERROR] {err}")
            self.close()
            return []

    def insert_one_user(self, user: dict) -> int:
        """
        Inserts a single user into the kw.TBL_USERS table.

        Parameters:
        - user (dict): Dictionary containing user fields.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_INSERT_ERROR on error.
        """
        user = self._filter_dict(user, kw.KW_LIST_USER)
        return self.__insert(kw.TBL_USERS, [user, ])

    def insert_users(self, users: list) -> int:
        """
        Inserts multiple users into the kw.TBL_USERS table.

        Parameters:
        - users (list): List of user dictionaries.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_INSERT_ERROR on error.
        """
        users = [self._filter_dict(user, kw.KW_LIST_USER) for user in users]
        return self.__insert(kw.TBL_USERS, users)

    def delete_users(self, condition: str) -> int:
        """
        Deletes users from the kw.TBL_USERS table based on a condition.

        Parameters:
        - condition (str): SQL WHERE condition.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_DELETE_ERROR on error.
        """
        return self.__delete(kw.TBL_USERS, condition)

    def select_users(self, condition: str = None) -> list:
        """
        Retrieves users from the kw.TBL_USERS table.

        Parameters:
        - condition (str, optional): SQL WHERE condition.

        Returns:
        - list: List of user records.
        """
        return self.__select(kw.TBL_USERS, condition)

    def update_users(self, updates: dict, condition: str) -> int:
        """
        Updates specific columns in the kw.TBL_USERS table based on a condition.

        Parameters:
        - updates (dict): Dictionary of column-value pairs to update.
        - condition (str): SQL WHERE condition to specify which rows to update.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_UPDATE_ERROR on error.
        """
        updates = self._filter_dict(updates, kw.KW_LIST_USER)
        return self.__update(kw.TBL_USERS, updates, condition)

    def count_users(self, condition: str = None) -> int:
        """
        Counts the number of users in the kw.TBL_USERS table.

        Parameters:
        - condition (str, optional): SQL WHERE condition.

        Returns:
        - int: The number of users, or -1 on error.
        """
        return self.__count(kw.TBL_USERS, condition)

    # Patients
    def get_patients(self, patient_id: int = kw.V_NULL, medic_id: int = kw.V_NULL) -> list:
        """
        Fetches patient records using the stored procedure `get_patient`.

        If `patient_id` is provided (not kw.V_NULL), fetches the specific patient by ID.
        Otherwise, it fetches all patients whose `lekar_id` (medic/doctor ID) matches `medic_id`.

        :parameter
         - patient_id: ID of the specific patient to retrieve, or kw.V_NULL to ignore.
         - medic_id: ID of the medic to filter patients by, if `patient_id` is kw.V_NULL.
        :return: A list of tuples representing the fetched patient records.
        """
        try:
            sql = "CALL get_patient(%s, %s)"
            self.cursor.execute(sql, (patient_id, medic_id))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"[SELECT ERROR] {err}")
            self.close()
            return []

    def insert_one_patient(self, patient: dict) -> int:
        """
        Inserts a single patient into the kw.TBL_PATIENTS table.

        Parameters:
        - patient (dict): Dictionary containing patient fields.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_INSERT_ERROR on error.
        """
        patient = self._filter_dict(patient, kw.KW_LIST_PATIENT)
        return self.__insert(kw.TBL_PATIENTS, [patient, ])

    def insert_patients(self, patients: list) -> int:
        """
        Inserts multiple patients into the kw.TBL_PATIENTS table.

        Parameters:
        - patients (list): List of patient dictionaries.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_INSERT_ERROR on error.
        """
        patients = [self._filter_dict(patient, kw.KW_LIST_PATIENT) for patient in patients]
        return self.__insert(kw.TBL_PATIENTS, patients)

    def delete_patients(self, condition: str) -> int:
        """
        Deletes patients from the kw.TBL_PATIENTS table based on a condition.

        Parameters:
        - condition (str): SQL WHERE condition.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_DELETE_ERROR on error.
        """
        return self.__delete(kw.TBL_PATIENTS, condition)

    def select_patients(self, condition: str = None) -> list:
        """
        Retrieves patients from the kw.TBL_PATIENTS table.

        Parameters:
        - condition (str, optional): SQL WHERE condition.

        Returns:
        - list: List of patient records.
        """
        return self.__select(kw.TBL_PATIENTS, condition)

    def update_patients(self, updates: dict, condition: str) -> int:
        """
        Updates specific columns in the kw.TBL_PATIENTS table based on a condition.

        Parameters:
        - updates (dict): Dictionary of column-value pairs to update.
        - condition (str): SQL WHERE condition to specify which rows to update.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_UPDATE_ERROR on error.
        """
        updates = self._filter_dict(updates, kw.KW_LIST_PATIENT)
        return self.__update(kw.TBL_PATIENTS, updates, condition)

    def count_patients(self, condition: str = None) -> int:
        """
        Counts the number of patients in the kw.TBL_PATIENTS table.

        Parameters:
        - condition (str, optional): SQL WHERE condition.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_COUNT_ERROR on error.
        """
        return self.__count(kw.TBL_PATIENTS, condition)

    # Original images
    def get_original_images(self, image_id: int = kw.V_NULL, patient_id: int = kw.V_NULL) -> list[dict]:
        """
        Database query to retrieve original images from the kw.TBL_IMAGES table. If none parameter filled, returns
        all processed images.

        Parameters:
        - image_id (int, optional): ID of the image to retrieve (first to check).
        - patient_id (int, optional): ID of the patient to retrieve (second to check).

        Returns:
        - list[dict]: List of processed image records.
        """
        try:
            sql = f"CALL get_original_image(%s, %s)"
            self.cursor.execute(sql, (image_id, patient_id))
            images = self.cursor.fetchall()
            diagnoses_names = {}
            diagnoses_ids = {}
            for image in images:
                diagnoses_names.setdefault(image[kw.KW_IMAGE_ID], []).append(image.get(kw.KW_DIAGNOSIS_NAME, kw.V_EMPTY_STRING))
                diagnoses_ids.setdefault(image[kw.KW_IMAGE_ID], []).append(image.get(kw.KW_DIAGNOSIS_ID, kw.V_EMPTY_INT))

            new_images = []
            for image in images:
                image_id = image[kw.KW_IMAGE_ID]
                if image_id in diagnoses_names.keys():
                    new_images.append({**image, kw.KW_DIAGNOSIS_NAME: diagnoses_names[image_id], kw.KW_DIAGNOSIS_ID: diagnoses_ids[image_id]})
                    diagnoses_ids.pop(image_id)
                    diagnoses_names.pop(image_id)
            return new_images

        except mysql.connector.Error as err:
            print(f"[SELECT ERROR] {err}")
            self.close()
            return []

    def insert_one_original_image(self, image: dict) -> int:
        """
        Inserts a single original image into the kw.TBL_IMAGES table.

        Parameters:
        - image (dict): Dictionary containing image fields.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_INSERT_ERROR on error.
        """
        image = self._filter_dict(image, kw.KW_LIST_IMAGE)
        return self.__insert(kw.TBL_IMAGES, [image, ])

    def insert_original_images(self, images: list) -> int:
        """
        Inserts multiple images into the kw.TBL_IMAGES table.

        Parameters:
        - images (list): List of image dictionaries.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_INSERT_ERROR on error.
        """
        images = [self._filter_dict(image, kw.KW_LIST_IMAGE) for image in images]
        return self.__insert(kw.TBL_IMAGES, images)

    def delete_original_images(self, condition: str) -> int:
        """
        Deletes images from the kw.TBL_IMAGES table based on a condition.

        Parameters:
        - condition (str): SQL WHERE condition.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_DELETE_ERROR on error.
        """
        return self.__delete(kw.TBL_IMAGES, condition)

    def select_original_images(self, condition: str = None) -> list:
        """
        Retrieves images from the kw.TBL_IMAGES table.

        Parameters:
        - condition (str, optional): SQL WHERE condition.

        Returns:
        - list: List of original image records.
        """
        return self.__select(kw.TBL_IMAGES, condition)

    def update_original_images(self, updates: dict, condition: str) -> int:
        """
        Updates specific columns in the kw.TBL_IMAGES table based on a condition.

        Parameters:
        - updates (dict): Dictionary of column-value pairs to update.
        - condition (str): SQL WHERE condition to specify which rows to update.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_UPDATE_ERROR on error.
        """
        updates = self._filter_dict(updates, kw.KW_LIST_IMAGE)
        return self.__update(kw.TBL_IMAGES, updates, condition)

    def count_original_images(self, condition: str = None) -> int:
        """
        Counts the number of images in the kw.TBL_IMAGES table.

        Parameters:
        - condition (str, optional): SQL WHERE condition.

        Returns:
        - int: The number of images, or -1 on error.
        """
        return self.__count(kw.TBL_IMAGES, condition)

    # Processed images
    def get_processed_images(self, image_id: int = kw.V_NULL, oimage_id: int = kw.V_NULL, patient_id: int = kw.V_NULL) -> list:
        """
        Database query to retrieve processed images from the kw.TBL_PIMAGES table. If none parameter filled, returns
        all processed images.

        Parameters:
        - image_id (int, optional): ID of the image to retrieve (first to check).
        - oimage_id (int, optional): ID of the original image to retrieve (second to check).
        - patient_id (int, optional): ID of the patient to retrieve (third to check).

        Returns:
        - list: List of processed image records.
        """
        try:
            sql = f"CALL get_processed_image(%s, %s, %s)"
            self.cursor.execute(sql, (image_id, oimage_id, patient_id))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"[SELECT ERROR] {err}")
            self.close()
            return []

    def insert_one_processed_image(self, processed_image: dict) -> int:
        """
        Inserts a single processed image into the kw.TBL_PIMAGES table.

        Parameters:
        - processed image (dict): Dictionary containing image fields.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_INSERT_ERROR on error.
        """
        processed_image = self._filter_dict(processed_image, kw.KW_LIST_PIMAGE)
        return self.__insert(kw.TBL_PIMAGES, [processed_image, ])

    def insert_processed_images(self, processed_images: list) -> int:
        """
        Inserts multiple images into the kw.TBL_PIMAGES table.

        Parameters:
        - processed_images (list): List of image dictionaries.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_INSERT_ERROR on error.
        """
        processed_images = [self._filter_dict(image, kw.KW_LIST_PIMAGE) for image in processed_images]
        return self.__insert(kw.TBL_PIMAGES, processed_images)

    def delete_processed_images(self, condition: str) -> int:
        """
        Deletes images from the kw.TBL_PIMAGES table based on a condition.

        Parameters:
        - condition (str): SQL WHERE condition.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_DELETE_ERROR on error.
        """
        return self.__delete(kw.TBL_PIMAGES, condition)

    def select_processed_images(self, condition: str = None) -> list:
        """
        Retrieves images from the kw.TBL_PIMAGES table.

        Parameters:
        - condition (str, optional): SQL WHERE condition.

        Returns:
        - list: List of processed image records.
        """
        return self.__select(kw.TBL_PIMAGES, condition)

    def update_processed_images(self, updates: dict, condition: str) -> int:
        """
        Updates specific columns in the kw.TBL_PIMAGES table based on a condition.

        Parameters:
        - updates (dict): Dictionary of column-value pairs to update.
        - condition (str): SQL WHERE condition to specify which rows to update.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_UPDATE_ERROR on error.
        """
        updates = self._filter_dict(updates, kw.KW_LIST_PIMAGE)
        return self.__update(kw.TBL_PIMAGES, updates, condition)

    def count_processed_images(self, condition: str = None) -> int:
        """
        Counts the number of images in the kw.TBL_PIMAGES table.

        Parameters:
        - condition (str, optional): SQL WHERE condition.

        Returns:
        - int: The number of images, or -1 on error.
        """
        return self.__count(kw.TBL_PIMAGES, condition)

    # Devices
    def insert_one_device(self, device: dict) -> int:
        """
        Inserts a single device into the kw.TBL_DEVICES table.

        Parameters:
        - device (dict): Dictionary containing device fields.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_INSERT_ERROR on error.
        """
        device = self._filter_dict(device, kw.KW_LIST_DEVICE)
        return self.__insert(kw.TBL_DEVICES, [device, ])

    def insert_devices(self, devices: list) -> int:
        """
        Inserts multiple devices into the kw.TBL_DEVICES table.

        Parameters:
        - devices (list): List of device dictionaries.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_INSERT_ERROR on error.
        """
        devices = [self._filter_dict(device, kw.KW_LIST_DEVICE) for device in devices]
        return self.__insert(kw.TBL_DEVICES, devices)

    def delete_devices(self, condition: str) -> int:
        """
        Deletes devices from the kw.TBL_DEVICES table based on a condition.

        Parameters:
        - condition (str): SQL WHERE condition.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_DELETE_ERROR on error.
        """
        return self.__delete(kw.TBL_DEVICES, condition)

    def select_devices(self, condition: str = None) -> list:
        """
        Retrieves devices from the kw.TBL_DEVICES table.

        Parameters:
        - condition (str, optional): SQL WHERE condition.

        Returns:
        - list: List of device records.
        """
        return self.__select(kw.TBL_DEVICES, condition)

    def update_devices(self, updates: dict, condition: str) -> int:
        """
        Updates specific columns in the kw.TBL_DEVICES table based on a condition.

        Parameters:
        - updates (dict): Dictionary of column-value pairs to update.
        - condition (str): SQL WHERE condition to specify which rows to update.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_UPDATE_ERROR on error.
        """
        updates = self._filter_dict(updates, kw.KW_LIST_DEVICE)
        return self.__update(kw.TBL_DEVICES, updates, condition)

    def count_devices(self, condition: str = None) -> int:
        """
        Counts the number of devices in the kw.TBL_DEVICES table.

        Parameters:
        - condition (str, optional): SQL WHERE condition.

        Returns:
        - int: The number of devices, or -1 on error.
        """
        return self.__count(kw.TBL_DEVICES, condition)
    
    # Roles
    def insert_one_role(self, role: dict) -> int:
        """
        Inserts a single role into the kw.TBL_ROLES table.

        Parameters:
        - role (dict): Dictionary containing role fields.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_INSERT_ERROR on error.
        """
        role = self._filter_dict(role, kw.KW_LIST_ROLE)
        return self.__insert(kw.TBL_ROLES, [role, ])

    def insert_roles(self, roles: list) -> int:
        """
        Inserts multiple roles into the kw.TBL_ROLES table.

        Parameters:
        - roles (list): List of role dictionaries.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_INSERT_ERROR on error.
        """
        roles = [self._filter_dict(role, kw.KW_LIST_ROLE) for role in roles]
        return self.__insert(kw.TBL_ROLES, roles) 
    
    def delete_roles(self, condition: str) -> int:
        """
        Deletes roles from the kw.TBL_ROLES table based on a condition.

        Parameters:
        - condition (str): SQL WHERE condition.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_DELETE_ERROR on error.
        """
        return self.__delete(kw.TBL_ROLES, condition)
    
    def select_roles(self, condition: str = None) -> list:
        """
        Retrieves roles from the kw.TBL_ROLES table.

        Parameters:
        - condition (str, optional): SQL WHERE condition.

        Returns:
        - list: List of user records.
        """
        return self.__select(kw.TBL_ROLES, condition)
    
    def update_roles(self, updates: dict, condition: str) -> int:
        """
        Updates specific columns in the kw.TBL_ROLES table based on a condition.

        Parameters:
        - updates (dict): Dictionary of column-value pairs to update.
        - condition (str): SQL WHERE condition to specify which rows to update.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_UPDATE_ERROR on error.
        """
        updates = self._filter_dict(updates, kw.KW_LIST_ROLE)
        return self.__update(kw.TBL_ROLES, updates, condition)

    def count_roles(self, condition: str = None) -> int:
        """
        Counts the number of roles in the kw.TBL_ROLES table.

        Parameters:
        - condition (str, optional): SQL WHERE condition.

        Returns:
        - int: The number of roles, or -1 on error.
        """
        return self.__count(kw.TBL_ROLES, condition)

    @staticmethod
    def get_role_by_id(role_id: int) -> [str, None]:
        """
        Retrieves a role name from the kw.TBL_ROLES table based on its ID.

        Parameters:
        - role_id (int): ID of the role to retrieve.

        Returns:
        - str: Role name if found, None otherwise.
        """
        db = Database()
        try:
            role = db.select_roles(f"{kw.KW_ROLE_ID} = {role_id}")[0]
            db.close()
            return role[kw.KW_ROLE_NAME]
        except IndexError:
            db.close()
            return None

    @staticmethod
    def get_role_id_by_name(role_name: str) -> [int, None]:
        """
        Retrieves a role ID from the kw.TBL_ROLES table based on its name.

        Parameters:
        - role_name (str): Name of the role to retrieve.

        Returns:
        - int: Role ID if found, None otherwise.
        """
        db = Database()
        try:
            role = db.select_roles(f"{kw.KW_ROLE_NAME} = '{role_name}'")[0]
            db.close()
            return role[kw.KW_ROLE_ID]
        except IndexError:
            db.close()
            return None

    # Methods
    def insert_one_method(self, method: dict) -> int:
        """
        Inserts a single method into the kw.TBL_METHODS table.

        Parameters:
        - method (dict): Dictionary containing method fields.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_INSERT_ERROR on error.
        """
        method = self._filter_dict(method, kw.KW_LIST_METHOD)
        return self.__insert(kw.TBL_METHODS, [method, ])

    def insert_methods(self, methods: list) -> int:
        """
        Inserts multiple methods into the kw.TBL_METHODS table.

        Parameters:
        - methods (list): List of method dictionaries.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_INSERT_ERROR on error.
        """
        methods = [self._filter_dict(method, kw.KW_LIST_METHOD) for method in methods]
        return self.__insert(kw.TBL_METHODS, methods)

    def delete_methods(self, condition: str) -> int:
        """
        Deletes methods from the kw.TBL_METHODS table based on a condition.

        Parameters:
        - condition (str): SQL WHERE condition.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_DELETE_ERROR on error.
        """
        return self.__delete(kw.TBL_METHODS, condition)

    def select_methods(self, condition: str = None) -> list:
        """
        Retrieves methods from the kw.TBL_METHODS table.

        Parameters:
        - condition (str, optional): SQL WHERE condition.

        Returns:
        - list: List of method records.
        """
        return self.__select(kw.TBL_METHODS, condition)

    def update_methods(self, updates: dict, condition: str) -> int:
        """
        Updates specific columns in the kw.TBL_METHODS table based on a condition.

        Parameters:
        - updates (dict): Dictionary of column-value pairs to update.
        - condition (str): SQL WHERE condition to specify which rows to update.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_UPDATE_ERROR on error.
        """
        updates = self._filter_dict(updates, kw.KW_LIST_METHOD)
        return self.__update(kw.TBL_METHODS, updates, condition)

    @staticmethod
    def get_method_by_id(method_id: int) -> [str, None]:
        """
        Retrieves a method name from the kw.TBL_METHODS table based on its ID.

        Parameters:
        - method_id (int): ID of the method to retrieve.

        Returns:
        - str: Method name if found, None otherwise.
        """
        db = Database()
        try:
            method = db.select_methods(f"{kw.KW_METHOD_ID} = {method_id}")[0]
            db.close()
            return method[kw.KW_METHOD_NAME]
        except IndexError:
            db.close()
            return None

    def count_methods(self, condition: str = None) -> int:
        """
        Counts the number of methods in the kw.TBL_METHODS table.

        Parameters:
        - condition (str, optional): SQL WHERE condition.

        Returns:
        - int: The number of methods, or -1 on error.
        """
        return self.__count(kw.TBL_METHODS, condition)

    # Diagnoses
    def insert_one_diagnose(self, diagnosis: dict) -> int:
        """
        Inserts a single diagnosis into the kw.TBL_DIAGNOSIS table.

        Parameters:
        - diagnosis (dict): Dictionary containing diagnosis fields.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_INSERT_ERROR on error.
        """
        diagnosis = self._filter_dict(diagnosis, kw.KW_LIST_DIAGNOSIS)
        return self.__insert(kw.TBL_DIAGNOSIS, [diagnosis, ])

    def insert_diagnoses(self, diagnoses: list) -> int:
        """
        Inserts multiple diagnoses into the kw.TBL_DIAGNOSIS table.

        Parameters:
        - diagnoses (list): List of diagnosis dictionaries.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_INSERT_ERROR on error.
        """
        diagnoses = [self._filter_dict(diagnosis, kw.KW_LIST_DIAGNOSIS) for diagnosis in diagnoses]
        return self.__insert(kw.TBL_DIAGNOSIS, diagnoses)

    def delete_diagnoses(self, condition: str) -> int:
        """
        Deletes diagnoses from the kw.TBL_DIAGNOSIS table based on a condition.

        Parameters:
        - condition (str): SQL WHERE condition.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_DELETE_ERROR on error.
        """
        return self.__delete(kw.TBL_DIAGNOSIS, condition)

    def select_diagnoses(self, condition: str = None) -> list:
        """
        Retrieves diagnoses from the kw.TBL_DIAGNOSIS table.

        Parameters:
        - condition (str, optional): SQL WHERE condition.

        Returns:
        - list: List of diagnosis records.
        """
        return self.__select(kw.TBL_DIAGNOSIS, condition)

    def update_diagnoses(self, updates: dict, condition: str) -> int:
        """
        Updates specific columns in the kw.TBL_DIAGNOSIS table based on a condition.

        Parameters:
        - updates (dict): Dictionary of column-value pairs to update.
        - condition (str): SQL WHERE condition to specify which rows to update.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_UPDATE_ERROR on error.
        """
        updates = self._filter_dict(updates, kw.KW_LIST_DIAGNOSIS)
        return self.__update(kw.TBL_DIAGNOSIS, updates, condition)

    def count_diagnoses(self, condition: str = None) -> int:
        """
        Counts the number of diagnoses in the kw.TBL_DIAGNOSIS table.

        Parameters:
        - condition (str, optional): SQL WHERE condition.

        Returns:
        - int: The number of diagnoses, or -1 on error.
        """
        return self.__count(kw.TBL_DIAGNOSIS, condition)

    @staticmethod
    def get_diagnose_by_id(diagnosis_id: int) -> [str, None]:
        """
        Retrieves a diagnosis name from the kw.TBL_DIAGNOSIS table based on its ID.

        Parameters:
        - diagnosis_id (int): ID of the diagnosis to retrieve.

        Returns:
        - str: Diagnosis name if found, None otherwise.
        """
        db = Database()
        try:
            diagnosis = db.select_diagnoses(f"{kw.KW_DIAGNOSIS_ID} = {diagnosis_id}")[0]
            db.close()
            return diagnosis[kw.KW_DIAGNOSIS_NAME]
        except IndexError:
            db.close()
            return None

    @staticmethod
    def get_diagnose_id_by_name(diagnosis_name: str) -> [int, None]:
        """
        Retrieves a diagnosis ID from the kw.TBL_DIAGNOSIS table based on its name.

        Parameters:
        - diagnosis_name (str): Name of the diagnosis to retrieve.

        Returns:
        - int: Diagnosis ID if found, None otherwise.
        """
        db = Database()
        try:
            diagnosis = db.select_diagnoses(f"{kw.KW_DIAGNOSIS_NAME} = '{diagnosis_name}'")[0]
            db.close()
            return diagnosis[kw.KW_DIAGNOSIS_ID]
        except IndexError:
            db.close()
            return None

    # Join table between originalne obrazy and diagnoses
    def insert_one_original_diagnose(self, original_diagnosis: dict) -> int:
        """
        Inserts a single original_diagnosis into the kw.TBL_ORIGINAL_DIAGNOSIS table.

        Parameters:
        - original_diagnosis (dict): Dictionary containing original_diagnosis fields.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_INSERT_ERROR on error.
        """
        return self.__insert(kw.TBL_ORIGINAL_DIAGNOSIS, [original_diagnosis, ])

    def insert_original_diagnoses(self, original_diagnoses: list) -> int:
        """
        Inserts multiple original_diagnoses into the kw.TBL_ORIGINAL_DIAGNOSIS table.

        Parameters:
        - original_diagnoses (list): List of original_diagnosis dictionaries.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_INSERT_ERROR on error.
        """
        return self.__insert(kw.TBL_ORIGINAL_DIAGNOSIS, original_diagnoses)

    def select_original_diagnoses(self, condition: str = None) -> list:
        """
        Retrieves original_diagnoses from the kw.TBL_ORIGINAL_DIAGNOSIS table.

        Parameters:
        - condition (str, optional): SQL WHERE condition.

        Returns:
        - list: List of original_diagnosis records.
        """
        return self.__select(kw.TBL_ORIGINAL_DIAGNOSIS, condition)

    def update_original_diagnoses(self, updates: dict, condition: str) -> int:
        """
        Updates specific columns in the kw.TBL_ORIGINAL_DIAGNOSIS table based on a condition.

        Parameters:
        - updates (dict): Dictionary of column-value pairs to update.
        - condition (str): SQL WHERE condition to specify which rows to update.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_UPDATE_ERROR on error.
        """
        return self.__update(kw.TBL_ORIGINAL_DIAGNOSIS, updates, condition)

    def count_original_diagnoses(self, condition: str = None) -> int:
        """
        Counts the number of original_diagnoses in the kw.TBL_ORIGINAL_DIAGNOSIS table.

        Parameters:
        - condition (str, optional): SQL WHERE condition.

        Returns:
        - int: The number of original_diagnoses, or -1 on error.
        """
        return self.__count(kw.TBL_ORIGINAL_DIAGNOSIS, condition)

    def delete_original_diagnoses(self, condition: str) -> int:
        """
        Deletes original_diagnoses from the kw.TBL_ORIGINAL_DIAGNOSIS table based on a condition.

        Parameters:
        - condition (str): SQL WHERE condition to specify which rows to delete.

        Returns:
        - int: ExitCodes.SUCCESS on success, ExitCodes.DATABASE_DELETE_ERROR on error.
        """
        return self.__delete(kw.TBL_ORIGINAL_DIAGNOSIS, condition)

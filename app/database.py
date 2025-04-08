import mysql.connector

"""
Uses:
 - db_is_ready: bool = database_object.is_ready()
 - success: int = database_object.insert_one_[user, patient, original_image, processed_image, device](data: dict)
 - success: int = database_object.insert_[users, patients, original_images, processed_images, devices](data: list[dict, ])
 - success: int = database_object.delete_[users, patients, original_images, processed_images, devices](SQL_condition: str)
 - found: list = database_object.select_[users, patients, original_images, processed_images, devices](SQL_condition: str)
 
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
            conn: Holds the connection object if successful, otherwise None.
            cursor: Holds the cursor object if successful, otherwise None.
        """

        # defining/creating connection with database
        self.conn = None
        self.cursor = None
        db_config = {
            # data for database connection (for now for test -> need to change)
            "host": "sql7.freesqldatabase.com",
            "user": "sql7771952",
            "password": "GFGQJXMZcM",
            "database": "sql7771952",
            "port": 3306
        }

        try:
            # Attempt to establish the connection
            self.conn = mysql.connector.connect(**db_config)

            # Check if the connection was successful before creating cursor
            if self.conn.is_connected():
                # defining cursor for interaction with database
                self.cursor = self.conn.cursor(dictionary=True)
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
        - int: 0 on success, 1 on error.
        """
        try:
            placeholders = ', '.join(['%s'] * len(data[0]))
            columns = ', '.join(data[0].keys())
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            values = [tuple(d.values()) for d in data]
            self.cursor.executemany(sql, values)
            self.conn.commit()
            return 0
        except mysql.connector.Error as err:
            print(f"[INSERT ERROR] {err}")
            return 1

    def __delete(self, table: str, condition: str) -> int:
        """
        Deletes records from a specified table based on a condition.

        Parameters:
        - table (str): The name of the table to delete from.
        - condition (str): SQL condition for selecting rows to delete.

        Returns:
        - int: 0 on success, 1 on error.
            """
        try:
            sql = f"DELETE FROM {table} WHERE {condition}"
            self.cursor.execute(sql)
            self.conn.commit()
            return 0
        except mysql.connector.Error as err:
            print(f"[DELETE ERROR] {err}")
            return 1

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
            return []

    # Users
    def insert_one_user(self, user: dict) -> int:
        """
        Inserts a single user into the 'uzivatelia' table.

        Parameters:
        - user (dict): Dictionary containing user fields.

        Returns:
        - int: 0 on success, 1 on error.
        """
        return self.__insert('uzivatelia', [user, ])

    def insert_users(self, users: list) -> int:
        """
        Inserts multiple users into the 'uzivatelia' table.

        Parameters:
        - users (list): List of user dictionaries.

        Returns:
        - int: 0 on success, 1 on error.
        """
        return self.__insert('uzivatelia', users)

    def delete_users(self, condition: str) -> int:
        """
        Deletes users from the 'uzivatelia' table based on a condition.

        Parameters:
        - condition (str): SQL WHERE condition.

        Returns:
        - int: 0 on success, 1 on error.
        """
        return self.__delete('uzivatelia', condition)

    def select_users(self, condition: str = None) -> list:
        """
        Retrieves users from the 'uzivatelia' table.

        Parameters:
        - condition (str, optional): SQL WHERE condition.

        Returns:
        - list: List of user records.
        """
        return self.__select('uzivatelia', condition)

    # Patients
    def insert_one_patient(self, patient: dict) -> int:
        """
        Inserts a single patient into the 'pacienti' table.

        Parameters:
        - patient (dict): Dictionary containing patient fields.

        Returns:
        - int: 0 on success, 1 on error.
        """
        return self.__insert('pacienti', [patient, ])

    def insert_patients(self, patients: list) -> int:
        """
        Inserts multiple patients into the 'pacienti' table.

        Parameters:
        - patients (list): List of patient dictionaries.

        Returns:
        - int: 0 on success, 1 on error.
        """
        return self.__insert('pacienti', patients)

    def delete_patients(self, condition: str) -> int:
        """
        Deletes patients from the 'pacienti' table based on a condition.

        Parameters:
        - condition (str): SQL WHERE condition.

        Returns:
        - int: 0 on success, 1 on error.
        """
        return self.__delete('pacienti', condition)

    def select_patients(self, condition: str = None) -> list:
        """
        Retrieves patients from the 'pacienti' table.

        Parameters:
        - condition (str, optional): SQL WHERE condition.

        Returns:
        - list: List of user records.
        """
        return self.__select('pacienti', condition)

    # Original images
    def insert_one_original_image(self, image: dict) -> int:
        """
        Inserts a single original image into the 'originalne_obrazy' table.

        Parameters:
        - image (dict): Dictionary containing image fields.

        Returns:
        - int: 0 on success, 1 on error.
        """
        return self.__insert('originalne_obrazy', [image, ])

    def insert_original_images(self, images: list) -> int:
        """
        Inserts multiple images into the 'originalne_obrazy' table.

        Parameters:
        - images (list): List of image dictionaries.

        Returns:
        - int: 0 on success, 1 on error.
        """
        return self.__insert('originalne_obrazy', images)

    def delete_original_images(self, condition: str) -> int:
        """
        Deletes images from the 'originalne_obrazy' table based on a condition.

        Parameters:
        - condition (str): SQL WHERE condition.

        Returns:
        - int: 0 on success, 1 on error.
        """
        return self.__delete('originalne_obrazy', condition)

    def select_original_images(self, condition: str = None) -> list:
        """
        Retrieves images from the 'originalne_obrazy' table.

        Parameters:
        - condition (str, optional): SQL WHERE condition.

        Returns:
        - list: List of user records.
        """
        return self.__select('originalne_obrazy', condition)

    # Processed images
    def insert_one_processed_images(self, processed_image: dict) -> int:
        """
        Inserts a single processed image into the 'spracovane_obrazy' table.

        Parameters:
        - processed image (dict): Dictionary containing image fields.

        Returns:
        - int: 0 on success, 1 on error.
        """
        return self.__insert('spracovane_obrazy', [processed_image, ])

    def insert_processed_images(self, processed_images: list) -> int:
        """
        Inserts multiple images into the 'spracovane_obrazy' table.

        Parameters:
        - processed_images (list): List of image dictionaries.

        Returns:
        - int: 0 on success, 1 on error.
        """
        return self.__insert('spracovane_obrazy', processed_images)

    def delete_processed_images(self, condition: str) -> int:
        """
        Deletes images from the 'spracovane_obrazy' table based on a condition.

        Parameters:
        - condition (str): SQL WHERE condition.

        Returns:
        - int: 0 on success, 1 on error.
        """
        return self.__delete('spracovane_obrazy', condition)

    def select_processed_images(self, condition: str = None) -> list:
        """
        Retrieves images from the 'spracovane_obrazy' table.

        Parameters:
        - condition (str, optional): SQL WHERE condition.

        Returns:
        - list: List of user records.
        """
        return self.__select('spracovane_obrazy', condition)

    # Devices
    def insert_one_device(self, device: dict) -> int:
        """
        Inserts a single device into the 'zariadenia' table.

        Parameters:
        - device (dict): Dictionary containing device fields.

        Returns:
        - int: 0 on success, 1 on error.
        """
        return self.__insert('zariadenia', [device, ])

    def insert_devices(self, devices: list) -> int:
        """
        Inserts multiple devices into the 'zariadenia' table.

        Parameters:
        - devices (list): List of device dictionaries.

        Returns:
        - int: 0 on success, 1 on error.
        """
        return self.__insert('zariadenia', devices)

    def delete_devices(self, condition: str) -> int:
        """
        Deletes devices from the 'zariadenia' table based on a condition.

        Parameters:
        - condition (str): SQL WHERE condition.

        Returns:
        - int: 0 on success, 1 on error.
        """
        return self.__delete('zariadenia', condition)

    def select_devices(self, condition: str = None) -> list:
        """
        Retrieves devices from the 'zariadenia' table.

        Parameters:
        - condition (str, optional): SQL WHERE condition.

        Returns:
        - list: List of user records.
        """
        return self.__select('zariadenia', condition)

    def close(self) -> int:
        """
        Closes the database connection and cursor.

        Returns:
        - int: 0 when successfully closed.
        """
        self.cursor.close()
        self.conn.close()
        return 0

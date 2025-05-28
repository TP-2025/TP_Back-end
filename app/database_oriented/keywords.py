# Table names
TBL_METHODS = "metody"
TBL_IMAGES = "originalne_obrazy"
TBL_PATIENTS = "pacienti"
TBL_ROLES = "role"
TBL_PIMAGES = "spracovane_obrazy"
TBL_USERS = "uzivatelia"
TBL_DEVICES = "zariadenia"
TBL_DIAGNOSIS = "diagnozy"
TBL_ORIGINAL_DIAGNOSIS = "originalne_obrazy_diagnozy"


# rights
ALLOWED_TO_ADD_PATIENTS = 1 << 0
ALLOWED_TO_ADD_MEDICS = 1 << 1
ALLOWED_TO_ADD_TECHNICS = 1 << 2
ALLOWED_TO_SEE_ALL_PATIENTS = 1 << 3
ALLOWED_TO_SEE_ALL_TECHNICS = 1 << 4
ALLOWED_TO_SEE_ALL_MEDICS = 1 << 5
ALLOWED_TO_SEE_ALL_ADMINS = 1 << 6
ALLOWED_TO_DELETE_PATIENTS = 1 << 7
ALLOWED_TO_DELETE_MEDICS = 1 << 8
ALLOWED_TO_DELETE_TECHNICS = 1 << 9
ALLOWED_TO_DELETE_ADMINS = 1 << 10
ALLOWED_TO_SEE_MEDICALS = 1 << 11
ALLOWED_TO_CHANGE_RIGHTS_FOR_MEDICS = 1 << 12
ALLOWED_TO_CHANGE_RIGHTS_FOR_TECHNICS = 1 << 13
ALLOWED_TO_CHANGE_ROLES = 1 << 14
ALLOWED_TO_ADD_IMAGES = 1 << 15

ALLOWED_ALL = (1 << 16) - 1

# Default values of empty data
V_EMPTY_STRING = "Nothing here"
V_EMPTY_INT = -1111
V_EMPTY_DICT = {"empty": "empty"}

# Remove value from database value
V_NULL = None

# roles
ROLE_ADMIN = "Admin"
ROLE_MEDIC = "Lekar"
ROLE_TECHNIC = "Technik"
ROLE_PATIENT = "Pacient"

# Keywords for accessing roles in database
KW_ROLE_ID = "id_r"
KW_ROLE_NAME = "nazov"

# Keywords for accessing users in database
KW_USER_ID = "id"
KW_USER_NAME = "meno"
KW_USER_SURNAME = "priezvisko"
KW_USER_EMAIL = "email"
KW_USER_HASHED_PASSWORD = "heslo_hash"
KW_USER_ROLE_ID = "rola_id"
KW_USER_RIGHTS = "prava"
KW_USER_SEX = "pohlavie"
KW_USER_YEAR_OF_BIRTH = "rok_narodenia"

# Keywords for accessing patient data in database
KW_PATIENT_ID = "pacient_id"
KW_PATIENT_DATE_OF_BIRTH = "datum_narodenia"
KW_PATIENT_MEDIC_ID = "lekar_id"
KW_PATIENT_USER_ID = "uzivatel_id"
KW_PATIENT_NOTE_MEDIC = "poznamky_lekara"
KW_PATIENT_DIAGNOSIS = "diagnoza"

# Keywords for accessing original image data in database
KW_IMAGE_ID = "id"
KW_IMAGE_PATIENT_ID = "pacient_id"
KW_IMAGE_DEVICE_ID = "zariadenie_id"
KW_IMAGE_PATH = "cesta_k_suboru"
KW_IMAGE_QUALITY = "kvalita"
KW_IMAGE_NOTE_TECHNIC = "technicke_pozn"
KW_IMAGE_NOTE_DIAGNOSIS = "diagnosticke_pozn"
KW_IMAGE_EYE = "oko"
KW_IMAGE_DATE = "datum_snimania"
KW_IMAGE_TECHNIC_ID = "technik_id"

# Keywords for accessing processed image data in database
KW_PIMAGE_ID = "id"  # TODO: check dictionary for overwrite with procedure get_processed_image
KW_PIMAGE_OIMAGE_ID = "originalny_obraz_id"
KW_PIMAGE_PATIENT_ID = "pacient_id"
KW_PIMAGE_USED_METHOD_ID = "metoda"
KW_PIMAGE_USED_METHOD_NAME = "metoda_meno"  # TODO: check dictionary for overwrite with procedure get_processed_image
KW_PIMAGE_RESULTS = "vystup"
KW_PIMAGE_METHOD_PARAMS = "parametre_metody"
KW_PIMAGE_STATE = "stav"
KW_PIMAGE_EYE = "oko"
KW_PIMAGE_QUALITY = "kvalita"
KW_PIMAGE_NOTE_TECHNIC = "popis_technika"
KW_PIMAGE_NOTE_MEDIC = "poznamky_lekara"
KW_PIMAGE_PATH = "cesta_k_obrazu"   # TODO: check whether the image is stored in the database

# Keywords for accessing methods in database
KW_METHOD_ID = "id"   # TODO: check dictionary for overwrite with procedure get_processed_image
KW_METHOD_NAME = "metoda"

# Keywords for accessing devices in database
KW_DEVICE_ID = "id"
KW_DEVICE_NAME = "nazov"
KW_DEVICE_TYPE = "typ"

# Keywords for accessing diagnoses in database
KW_DIAGNOSIS_ID = "id_diagnozy"
KW_DIAGNOSIS_NAME = "diagnoza"

# Keywords for accessing joints between tables originalne obraz and diagnoses in database
KW_OD_ID = "id_connect"
KW_OD_ORIGINAL_IMAGE_ID = "originalny_obraz_id"
KW_OD_DIAGNOSIS_ID = "diagnoza_id"


# Keyword lists
KW_LIST_USER = [KW_USER_NAME, KW_USER_SURNAME, KW_USER_EMAIL, KW_USER_HASHED_PASSWORD, KW_USER_ROLE_ID,
                KW_USER_RIGHTS, KW_USER_SEX, KW_USER_YEAR_OF_BIRTH]
KW_LIST_PATIENT = [KW_PATIENT_DATE_OF_BIRTH, KW_PATIENT_MEDIC_ID, KW_PATIENT_USER_ID, KW_PATIENT_NOTE_MEDIC,
                   KW_PATIENT_DIAGNOSIS]
KW_LIST_IMAGE = [KW_IMAGE_PATIENT_ID, KW_IMAGE_DEVICE_ID, KW_IMAGE_PATH, KW_IMAGE_QUALITY,
                 KW_IMAGE_NOTE_TECHNIC, KW_IMAGE_NOTE_DIAGNOSIS, KW_IMAGE_EYE, KW_IMAGE_DATE, KW_IMAGE_TECHNIC_ID]
KW_LIST_PIMAGE = [KW_PIMAGE_OIMAGE_ID, KW_PIMAGE_USED_METHOD_ID, KW_PIMAGE_RESULTS, KW_PIMAGE_METHOD_PARAMS,
                  KW_PIMAGE_STATE, KW_PIMAGE_QUALITY, KW_PIMAGE_NOTE_TECHNIC, KW_PIMAGE_NOTE_MEDIC,
                  KW_PIMAGE_PATH]
KW_LIST_DEVICE = [KW_DEVICE_NAME, KW_DEVICE_TYPE]
KW_LIST_ROLE = [KW_ROLE_NAME,]
KW_LIST_METHOD = [KW_METHOD_NAME,]
KW_LIST_DIAGNOSIS = [KW_DIAGNOSIS_NAME,]
KW_LIST_OD = [KW_OD_ORIGINAL_IMAGE_ID, KW_OD_DIAGNOSIS_ID]

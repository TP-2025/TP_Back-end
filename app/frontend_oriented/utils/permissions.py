from app.database_oriented.users.admin import Admin
from app.database_oriented.users.medic import Medic
from app.database_oriented.users.technic import Technic

PERMISSIONS = {
    "add_device": (Admin, Medic, Technic),
    "edit_device": (Admin),
    "delete_device":(Admin),
    "get_devices":(Admin, Medic, Technic),

    "add_additional_device": (Admin, Medic, Technic),
    "edit_additional_device": (Admin),
    "delete_additional_device": (Admin),
    "get_additional_devices": (Admin, Medic, Technic),

    "add_diagnosis": (Admin, Medic, Technic),
    "edit_diagnosis": (Admin),
    "delete_diagnosis": (Admin),
    "get_diagnosis": (Admin, Medic, Technic),

    "add_method": (Admin),
    "edit_method": (Admin),
    "delete_method": (Admin),
    "get_methods": (Admin, Medic),

    "add_picture": (Admin, Medic, Technic),
    "get_original_pictures": (Admin, Medic, Technic),
    "send_for_processing": (Admin, Medic),
    "get_processed_pictures": (Admin, Medic),


    "get_my_info": (Admin, Medic, Technic),

}
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class UserRole(enum.Enum):
    admin = "admin"
    doctor = "doctor"
    technician = "technician"

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.technician)  # default role is technician (for now)
    full_name = Column(String)
    is_active = Column(Integer, default=1)  # 1 means active, 0 means inactive
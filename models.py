from sqlalchemy import Column, String
from database import Base

# Database model
class User(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)


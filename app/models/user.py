from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.core.database import Base
from sqlalchemy.orm import Session
from datetime import datetime
from app.services.statistiche import create_statistiche

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hashed_password = Column(String, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True, default=datetime.now())
    is_superuser = Column(Boolean, nullable=False, default=False)
    username = Column(String(150), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, nullable=False, default=True)

    @staticmethod
    def create(username : str, password : str, db : Session):
        new_user = User(username=username, hashed_password=password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        create_statistiche(db, new_user.id)
        return new_user
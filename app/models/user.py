from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.core.database import Base
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.statistiche import Statistiche

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
        new_stella = Statistiche(utente_id=new_user.id, tipo_domanda='stelle', nr_errori=0)
        db.add(new_stella)
        db.commit()
        db.refresh(new_stella)
        return new_user
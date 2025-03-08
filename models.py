from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hashed_password = Column(String, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True, default=datetime.now())
    is_superuser = Column(Boolean, nullable=False, default=False)
    username = Column(String(150), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, nullable=False, default=True)

class TestsGroup(Base):
    __tablename__ = "testsgroup"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nr_test = Column(Integer, nullable=False)
    nr_gruppo = Column(Integer, nullable=False, default=0)
    tipo = Column(String(50), nullable=False, default='manuale')
    in_sequenza = Column(Boolean, nullable=False, default=True)
    secondi_ritardo = Column(Integer, nullable=False, default=5)
    data_ora_inizio = Column(DateTime(timezone=True), nullable=True, default=None)
    data_ora_inserimento = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    utente_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    utente = relationship("User")
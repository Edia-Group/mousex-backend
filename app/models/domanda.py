from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.core.database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import Session

class Domanda(Base):
    __tablename__ = "domande"

    id_domanda = Column(Integer, primary_key=True, index=True, autoincrement=True)
    corpo = Column(String(500), nullable=False)
    data_ora_inserimento = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    tipo = Column(String(50), nullable=False, default='select')
    numero_pagina = Column(Integer, nullable=True)
    attivo = Column(Boolean, nullable=False, default=True)
    risposta_esatta = Column(String(500), nullable=False)
    posizione = Column(Integer, nullable=True)

    def create(self, db : Session):
        db.add(self)
        db.commit()
        db.refresh(self)
        return self
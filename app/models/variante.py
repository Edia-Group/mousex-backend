from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from app.core.database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session

class Variante(Base):
    __tablename__ = "varianti"

    id_variante = Column(Integer, primary_key=True, index=True, autoincrement=True)
    corpo = Column(String, nullable=False, default={})
    data_ora_inserimento = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    tipo = Column(String(50), nullable=True, default='select')
    numero_pagina = Column(Integer, nullable=True)
    attivo = Column(Boolean, nullable=True, default=True)
    domanda_id = Column(Integer, ForeignKey("domande.id_domanda"), nullable=False)
    posizione = Column(Integer, nullable=False, default=0)

    utente = relationship("Domanda")

    def create(self, db : Session):
        db.add(self)
        db.commit()
        db.refresh(self)
        return self
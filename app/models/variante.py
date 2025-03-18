from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from app.core.database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Variante(Base):
    __tablename__ = "varianti"

    idVariante = Column(Integer, primary_key=True, index=True, autoincrement=True)
    corpo = Column(String(500), nullable=False)
    data_ora_inserimento = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    tipo = Column(String(50), nullable=True, default='select')
    numeroPagine = Column(Integer, nullable=True)
    attivo = Column(Boolean, nullable=True, default=True)
    domanda_id = Column(Integer, ForeignKey("domande.idDomanda"), nullable=False)
    rispostaEsatta = Column(String(500), nullable=False)

    utente = relationship("Domanda")

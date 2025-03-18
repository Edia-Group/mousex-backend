from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base
from sqlalchemy.orm import Session

class Statistiche(Base):
    __tablename__ = "statistiche"

    id = Column(Integer, primary_key=True, index=True)
    tipo_domanda = Column(String(50), nullable=False)
    nr_errori = Column(Integer, nullable=False)
    utente_id =  Column(Integer, ForeignKey("users.id"), nullable=False)

    def retrieve_stelle(utente_id : int, db : Session):
        return db.query(Statistiche).filter(Statistiche.utente_id == utente_id
                                            , Statistiche.tipo_domanda == 'stelle').first().nr_errori

        
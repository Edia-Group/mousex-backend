from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from app.core.database import Base
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy.sql import func

class Test(Base):
    __tablename__ = "tests"

    id_test = Column(Integer, primary_key=True, index=True, autoincrement=True)
    data_ora_inizio = Column(DateTime(), nullable=True)
    tipo = Column(String(50), nullable=False, default = 'Normale')
    in_sequenza = Column(Boolean, nullable=True, default=False)
    nr_gruppo = Column(Integer, nullable=False, default = 0)
    secondi_ritardo = Column(Integer, nullable=False, default=5)
    utente_id =  Column(Integer, ForeignKey("users.id"), nullable=False)
    data_ora_fine = Column(DateTime(), nullable=True)
    data_ora_inserimento = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    nr_test = Column(Integer, nullable=False, default =0)
    tempo_impiegato = Column(Float, nullable=True, default =0)
    malus_f5 = Column(Boolean, nullable=False, default=False)
    numero_errori = Column(Integer, nullable=False, default=0)
    is_validate = Column(Boolean, nullable=True, default=False)

    def save(self, db: Session):
        self.dataOraFine = datetime.now() + timedelta(hours=1) 
        if self.dataOraInizio:
            self.tempo_impiegato = float((self.dataOraFine - self.dataOraInizio).total_seconds())
        db.commit()
        db.refresh(self)
        return self

    def validate(self, db: Session):
        self.is_validate = True
        db.commit()
        db.refresh(self)
        return self
    
    @staticmethod
    def create(id : int, secondi_ritardo : int , tipo: str, db : Session):
        new_test = Test(utente_id = id, data_ora_inizio = datetime.now() + timedelta(seconds=secondi_ritardo) + timedelta(hours=1) , tipo = tipo)
        db.add(new_test)
        db.commit()
        db.refresh(new_test)
        return new_test
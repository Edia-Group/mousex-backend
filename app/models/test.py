from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from app.core.database import Base
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy.sql import func

class Test(Base):
    __tablename__ = "tests"

    idTest = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dataOraInizio = Column(DateTime(), nullable=True)
    tipo = Column(String(50), nullable=False, default = 'Normale')
    inSequenza = Column(Boolean, nullable=True, default=False)
    nrGruppo = Column(Integer, nullable=False, default = 0)
    secondiRitardo = Column(Integer, nullable=False, default=5)
    utente_id =  Column(Integer, ForeignKey("users.id"), nullable=False)
    dataOraFine = Column(DateTime(), nullable=True)
    dataOraInserimento = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    nrTest = Column(Integer, nullable=False, default =0)
    tempo_impiegato = Column(Float, nullable=True, default =0)
    malusF5 = Column(Boolean, nullable=False, default=False)
    numeroErrori = Column(Integer, nullable=False, default=0)
    is_validate = Column(Boolean, nullable=True, default=False)

    def save(self, db: Session):
        self.dataOraFine = datetime.now() 
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
    def create(id : int, db : Session):
        new_test = Test(utente_id = id, dataOraInizio = datetime.now() + timedelta(seconds=15))
        db.add(new_test)
        db.commit()
        db.refresh(new_test)
        return new_test
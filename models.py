from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base
from sqlalchemy.orm import relationship, Session
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

    def decrement(self, db : Session):
        self.nr_test -= 1
        db.commit()
        db.refresh()
        return self
    
class Test(Base):
    __tablename__ = "tests"

    idTest = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dataOraInizio = Column(DateTime(timezone=True), nullable=True)
    tipo = Column(String(50), nullable=False, default = 'Normale')
    inSequenza = Column(Boolean, nullable=True, default=False)
    nrGruppo = Column(Integer, nullable=False, default = 0)
    secondiRitardo = Column(Integer, nullable=False, default=5)
    utente_id =  Column(Integer, ForeignKey("users.id"), nullable=False)
    dataOraFine = Column(DateTime(timezone=True), nullable=True)
    dataOraInserimento = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    nrTest = Column(Integer, nullable=False, default =0)
    malusF5 = Column(Boolean, nullable=False, default=False)
    numeroErrori = Column(Integer, nullable=False, default=0)

    def save(self, db:Session):
        self.dataOraFine = datetime.now()
        db.commit()
        db.refresh(self)    
        return self
    
    @staticmethod
    def create(id : int, db : Session):
        new_test = Test(utente_id = id)
        db.add(new_test)
        db.commit()
        db.refresh(new_test)
        return new_test
    


class Domanda(Base):
    __tablename__ = "domande"

    idDomanda = Column(Integer, primary_key=True, index=True, autoincrement=True)
    corpo = Column(String(500), nullable=False)
    data_ora_inserimento = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    tipo = Column(String(50), nullable=False, default='select')
    numeroPagine = Column(Integer, nullable=True)
    attivo = Column(Boolean, nullable=False, default=True)

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

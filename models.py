from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from database import Base
from sqlalchemy.orm import relationship, Session
from datetime import datetime, timezone, timedelta

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
        db.refresh(self)
        return self
    
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

    def save(self, db: Session):
        self.dataOraFine = datetime.now() 
        if self.dataOraInizio:
            self.tempo_impiegato = float((self.dataOraFine - self.dataOraInizio).total_seconds())
        db.commit()
        db.refresh(self)
        return self
    
    @staticmethod
    def create(id : int, db : Session):
        new_test = Test(utente_id = id, dataOraInizio = datetime.now() )
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

class Statistiche(Base):
    __tablename__ = "statistiche"

    id = Column(Integer, primary_key=True, index=True)
    tipo_domanda = Column(String(50), nullable=False)
    nr_errori = Column(Integer, nullable=False)
    utente_id =  Column(Integer, ForeignKey("users.id"), nullable=False)

    def retrieve_stelle(utente_id : int, db : Session):
        return db.query(Statistiche).filter(Statistiche.utente_id == utente_id
                                            , Statistiche.tipo_domanda == 'stelle').first().nr_errori

        
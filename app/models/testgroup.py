from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from app.core.database import Base
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql import func

class TestsGroup(Base):
    __tablename__ = "testsgroup"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nr_test = Column(Integer, nullable=False)
    nr_gruppo = Column(Integer, nullable=False, default=0)
    tipo = Column(String(50), nullable=False, default='manuale')
    visibile = Column(Boolean, nullable=True, default=True)
    secondi_ritardo = Column(Integer, nullable=False, default=5)
    data_ora_inizio = Column(DateTime(timezone=True), nullable=True, default=None)
    data_ora_inserimento = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    utente_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    testprefattigroup_id = Column(Integer, ForeignKey("testsprefattigroup.id"), nullable=True)

    utente = relationship("User")

    def decrement(self, db : Session):
        if self.nr_test <= 1:
            db.delete(self)
            db.commit()
            return True
        self.nr_test -= 1
        db.commit()
        db.refresh(self)
        return False
    
    def create(self, db:Session):
        db.add(self)
        db.commit()
        db.refresh(self)
        return self
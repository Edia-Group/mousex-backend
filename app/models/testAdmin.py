from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey
from app.core.database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import Session

class TestAdmin(Base):
    __tablename__ = "test_admin"

    id_test_admin = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_test = Column(Integer, ForeignKey("tests.id_test"), nullable=False)
    data_ora_inserimento = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    attivo = Column(Boolean, nullable=True, default=True)
    id_domanda = Column(Integer, ForeignKey("domande.id_domanda"), nullable=False)

    def create(self, db : Session):
        db.add(self)
        db.commit()
        db.refresh(self)
        return self
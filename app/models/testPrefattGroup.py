from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.core.database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import Session

class TestPrefattiGroup(Base):
    __tablename__ = "testsprefattigroup"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(50), nullable=False, default='prima selezione')
    generated = Column(Boolean, nullable=False, default=False)
    visible = Column(Boolean, nullable=False, default=False)
    data_ora_inserimento = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    @staticmethod
    def create(nome: str, db : Session):
        new_testgroup_prefatto = (TestPrefattiGroup(nome=nome))
        db.add(new_testgroup_prefatto)
        db.commit()
        db.refresh(new_testgroup_prefatto)
        return new_testgroup_prefatto

    def change_visibility(id: int, db : Session):
        testgroup = db.query(TestPrefattiGroup).filter(TestPrefattiGroup.id == id).first()
        testgroup.visible = not testgroup.visible
        db.commit()
        db.refresh(testgroup)
        return testgroup
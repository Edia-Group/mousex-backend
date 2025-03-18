from fastapi import APIRouter, Depends, HTTPException
from app.schemas.testgroup import TestsGroupWithUser, TestsGroupCreate, TestsGroupDelete
from app.models.testgroup import TestsGroup
from app.core.security import oauth2_scheme
from sqlalchemy.orm import Session
from app.core.database import get_db
from typing import List
from app.utils.auth import get_username_from_token
from datetime import datetime
from app.schemas.testgroup import TestsGroupDeleteAll
from app.models.domanda import Domanda
from app.models.variante import Variante
from app.schemas.test import TestAdminCreate

testgroup_router = APIRouter(
    prefix="/testsgroup", 
    tags=["TestsGroup"],   
    responses={404: {"description": "Not found"}},
    )

@testgroup_router.post("/create")
def create_tests_group(tests_group: TestsGroupCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    user = get_username_from_token(token, db)
    db_tests_group = TestsGroup(**tests_group.model_dump(), utente_id=user.id, data_ora_inserimento = datetime.now()) 
    db_tests_group.create(db)
    return db_tests_group

@testgroup_router.post("/delete")
def delete_tests_group(tests_group: TestsGroupDelete, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    user = get_username_from_token(token, db)
    db_tests_group = db.query(TestsGroup).filter(TestsGroup.utente_id == user.id, TestsGroup.id==tests_group.id).first()
    if db_tests_group:
        db.delete(db_tests_group)
        db.commit()
    return db_tests_group


@testgroup_router.post("/delete_all")
def delete_all_tests_group(tests_group: TestsGroupDeleteAll, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = get_username_from_token(token, db)
    deleted_count = db.query(TestsGroup).filter(
        TestsGroup.utente_id == user.id, 
        TestsGroup.tipo==tests_group.tipo
    ).delete(synchronize_session=False)
    
    db.commit()
    return {"deleted_count": deleted_count}

@testgroup_router.get("/all", response_model= List[TestsGroupWithUser] )
def read_tests_group(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    user = get_username_from_token(token, db)
    db_tests_group = db.query(TestsGroup).filter(TestsGroup.utente_id== user.id).all()
    return db_tests_group

@testgroup_router.get("/decrement/{id_TestGroup}", response_model= TestsGroupWithUser)
def decrement_testgroup(id_TestGroup :int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    user = get_username_from_token(token, db)
    db_tests_group = db.query(TestsGroup).filter(TestsGroup.utente_id== user.id, TestsGroup.id == id_TestGroup).first()
    if db_tests_group:
        db_tests_group.decrement(db)
    return db_tests_group

@testgroup_router.post("/admin-creation")
def create_test(test: TestAdminCreate, db: Session = Depends(get_db)):
    try:
        for pagina in test.pagine:
            for domanda_data in pagina.domande:
                domanda = Domanda(corpo=domanda_data.corpo)
                db.add(domanda)
                db.flush() 
                db.refresh(domanda)

                variante_corretta = Variante(
                    corpo=domanda_data.risposta_corretta,
                    domanda_id=domanda.idDomanda,
                    rispostaEsatta=domanda_data.risposta_corretta
                )
                db.add(variante_corretta)

                for opzione in domanda_data.altre_opzioni:
                    variante_opzione = Variante(
                        corpo=opzione,
                        domanda_id=domanda.idDomanda,
                        rispostaEsatta=domanda_data.risposta_corretta
                    )
                    db.add(variante_opzione)
        db.commit()
        return {"message": "Test created successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

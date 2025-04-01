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
from app.schemas.domande import DomandaRisposta
from app.services.test import generate_test

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

@testgroup_router.get("/{id_testsgroup}/new_test", response_model=DomandaRisposta)
def new_test(id_testsgroup: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    user = get_username_from_token(token, db)
    db_tests_group = db.query(TestsGroup).filter(TestsGroup.utente_id == user.id, TestsGroup.id==id_testsgroup).first()
    if not db_tests_group:
        raise HTTPException(status_code=404, detail="TestGroup not found")
    db_tests_group.decrement(db)
    """
    if db.tests_group.tipo == "prefatto":
    TODO ecc
    """
    return generate_test(db_tests_group, user, db)



@testgroup_router.post("/delete")
def delete_tests_group(tests_group: TestsGroupDelete, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    user = get_username_from_token(token, db)
    db_tests_group = db.query(TestsGroup).filter(TestsGroup.utente_id == user.id, TestsGroup.id==tests_group.id).first()
    if db_tests_group:
        db_tests_group.visibile = False
        db.commit()
        db.refresh(db_tests_group)
    return db_tests_group


@testgroup_router.post("/delete_all")
def delete_all_tests_group(tests_group: TestsGroupDeleteAll, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = get_username_from_token(token, db)
    deleted_count = db.query(TestsGroup).filter(
        TestsGroup.utente_id == user.id, 
        TestsGroup.tipo == tests_group.tipo
    ).update({TestsGroup.visibile: False}, synchronize_session=False)
    
    db.commit()
    return {"deleted_count": deleted_count}

@testgroup_router.get("/all", response_model= List[TestsGroupWithUser] )
def read_tests_group(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    user = get_username_from_token(token, db)
    db_tests_group = db.query(TestsGroup).filter(TestsGroup.utente_id== user.id, TestsGroup.visibile == True).all()
    return db_tests_group

@testgroup_router.get("/all_triggered", response_model= List[TestsGroupWithUser] )
def read_tests_group(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    user = get_username_from_token(token, db)
    db_tests_group = db.query(TestsGroup).filter(
        TestsGroup.utente_id == user.id, 
        TestsGroup.visibile == True, 
    ).all()

    db_tests_group = [test_group for test_group in db_tests_group if ('triggered' in test_group.tipo)]
    return db_tests_group

@testgroup_router.get("/decrement/{id_TestGroup}", response_model= TestsGroupWithUser)
def decrement_testgroup(id_TestGroup :int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    user = get_username_from_token(token, db)
    db_tests_group = db.query(TestsGroup).filter(TestsGroup.utente_id== user.id, TestsGroup.id == id_TestGroup).first()
    if db_tests_group:
        db_tests_group.decrement(db)
    return db_tests_group

@testgroup_router.get("/get/{id_TestGroup}", response_model= TestsGroupWithUser)
def decrement_testgroup(id_TestGroup :int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    user = get_username_from_token(token, db)
    db_tests_group = db.query(TestsGroup).filter(TestsGroup.utente_id== user.id, TestsGroup.id == id_TestGroup).first()
    if not db_tests_group:
        raise HTTPException(status_code=404, detail="TestGroup not found")
    return db_tests_group

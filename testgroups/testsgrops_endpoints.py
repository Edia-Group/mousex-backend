from fastapi import APIRouter, Depends
from testgroups.testgroups_schemas import TestsGroupWithUser, TestsGroupCreate, TestsGroupDelete
from models import TestsGroup
from security import oauth2_scheme
from sqlalchemy.orm import Session
from database import get_db
from typing import List
from autentication.auth_utils import SECRET_KEY, ALGORITHM
from autentication.auth_utils import get_username_from_token

testgroup_router = APIRouter(
    prefix="/testsgroup", 
    tags=["TestsGroup"],   
    responses={404: {"description": "Not found"}},
    )

@testgroup_router.post("/create")
def create_tests_group(tests_group: TestsGroupCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    username , id = get_username_from_token(token, db)
    db_tests_group = TestsGroup(**tests_group.model_dump(), utente_id=id) 
    db.add(db_tests_group)
    db.commit()
    db.refresh(db_tests_group)
    return db_tests_group

@testgroup_router.post("/delete")
def delete_tests_group(tests_group: TestsGroupDelete, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    username , id = get_username_from_token(token, db)
    db_tests_group = db.query(TestsGroup).filter(TestsGroup.utente_id == id, TestsGroup.id==tests_group.id).first()
    if db_tests_group:
        db.delete(db_tests_group)
        db.commit()
    return db_tests_group

@testgroup_router.get("/all", response_model= List[TestsGroupWithUser] )
def read_tests_group(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    username, id = get_username_from_token(token, db)
    db_tests_group = db.query(TestsGroup).filter(TestsGroup.utente_id== id).all()
    return db_tests_group

@testgroup_router.get("/decrement/{id_TestGroup}", response_model= List[TestsGroupWithUser] )
def decrement_testgroup(id_TestGroup :int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    username, id = get_username_from_token(token, db)
    db_tests_group = db.query(TestsGroup).filter(TestsGroup.utente_id== id, TestsGroup.id == id_TestGroup).first()
    if db_tests_group:
        db_tests_group.decrement()
    return db_tests_group

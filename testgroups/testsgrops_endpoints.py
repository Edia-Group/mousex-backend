from fastapi import APIRouter, HTTPException, Depends, status
from testgroups.testgroups_schemas import TestsGroupWithUser, TestsGroupCreate
import models
from security import oauth2_scheme
from sqlalchemy.orm import Session
from database import get_db
from typing import List
from autentication.auth_utils import SECRET_KEY, ALGORITHM
import jwt

testgroup_router = APIRouter(
    prefix="/testsgroup", 
    tags=["TestsGroup"],   
    responses={404: {"description": "Not found"}},
    )

@testgroup_router.post("/create")
def create_tests_group(tests_group: TestsGroupCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("sub")
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_tests_group = models.TestsGroup(**tests_group.model_dump(), utente_id=user.id) 
    db.add(db_tests_group)
    db.commit()
    db.refresh(db_tests_group)
    return db_tests_group

@testgroup_router.get("/tests_groups", response_model= List[TestsGroupWithUser] )
def read_tests_group(tests_group_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    db_tests_group = db.query(models.TestsGroup).filter(models.TestsGroup.id == tests_group_id).all()

    return db_tests_group


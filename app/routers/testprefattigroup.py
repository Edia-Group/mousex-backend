from fastapi import APIRouter, Depends, HTTPException
from app.schemas.testprefattigroup import TestPrefattiGroupBase
from app.core.security import oauth2_scheme
from sqlalchemy.orm import Session
from app.core.database import get_db
from typing import List
from app.models.testPrefattGroup import TestPrefattiGroup
from app.models.testgroup import TestsGroup
from app.utils.auth import get_username_from_token
from datetime import datetime, timedelta
from app.models.test import Test
from app.schemas.test import TestBase
from app.models.user import User

testprefattigroup_router = APIRouter(
    prefix="/testprefattigroup",
    tags=["TestPrefattiGroup"], 
    responses={404: {"description": "Not found"}},
    )

@testprefattigroup_router.get("/all", response_model= List[TestPrefattiGroupBase] )
def read_tests_group(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    return db.query(TestPrefattiGroup).all()


@testprefattigroup_router.get("/create/{nome_testgroup_prefatto}", response_model= TestPrefattiGroupBase )
def read_tests_group(nome_testgroup_prefatto : str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    user = get_username_from_token(token, db)
    new_testprefattogroup =  TestPrefattiGroup.create(nome_testgroup_prefatto, db)
    new_testgroup_associated = TestsGroup.create(
        TestsGroup(
            nr_test = 0,
            tipo = 'prefatto',
            utente_id = user.id,
            testprefattigroup_id = new_testprefattogroup.id,
            data_ora_inserimento = datetime.now() + timedelta(hours=1)
        ),
        db
    )
    return new_testprefattogroup

@testprefattigroup_router.get("/change_visibility/{id_testgroup_prefatto}", response_model= TestPrefattiGroupBase )
def read_tests_group(id_testgroup_prefatto : str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    return TestPrefattiGroup.change_visibility(id_testgroup_prefatto, db)

@testprefattigroup_router.get("/trigger/{id_testgroup_prefatto}")
def read_tests_group(id_testgroup_prefatto : str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    test_prefatto = db.query(TestPrefattiGroup).filter(TestPrefattiGroup.id == id_testgroup_prefatto).first()
    if not test_prefatto:
        raise HTTPException(status_code=404, detail="Test prefatto group not found")
    if test_prefatto.generated:
        raise HTTPException(status_code=400, detail="Test prefatto group already triggered")
    test_group_associated = db.query(TestsGroup).filter(TestsGroup.testprefattigroup_id == id_testgroup_prefatto).first()
    if not test_group_associated:
        raise HTTPException(status_code=404, detail="Associated test group not found")
    existing_users = db.query(User).all()
    new_testsgroup = [
        TestsGroup(
            nr_test=test_group_associated.nr_test,
            tipo=f'prefatto {test_prefatto.nome} triggere',
            utente_id=user.id,
            testprefattigroup_id=test_prefatto.id,
            data_ora_inserimento=datetime.now() + timedelta(hours=1),
        )
        for user in existing_users
    ]
    test_prefatto.generated = True
    db.commit()
    db.refresh(test_prefatto)
    db.bulk_save_objects(new_testsgroup)
    db.commit()
    return {"Success": "Test group triggered successfully"}

@testprefattigroup_router.get("/associated_test/{id_testgroup_prefatto}" ,response_model= List[TestBase] )
def read_tests_group(id_testgroup_prefatto : str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    user = get_username_from_token(token, db)
    associated_testgroup = db.query(TestsGroup).filter(TestsGroup.testprefattigroup_id == id_testgroup_prefatto).first()
    associated_test = db.query(Test).filter(Test.testgroup_id == associated_testgroup.id).all()

    return associated_test

@testprefattigroup_router.delete("/delete/{id_testgroup_prefatto}")
def read_tests_group(id_testgroup_prefatto : str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    user = get_username_from_token(token, db)

    # Delete all associated tests
    test_prefatto = db.query(TestPrefattiGroup).filter(TestPrefattiGroup.id == id_testgroup_prefatto).first()
    associated_testgroup = db.query(TestsGroup).filter(TestsGroup.testprefattigroup_id == id_testgroup_prefatto).all()
    if test_prefatto is None:
        raise HTTPException(status_code=404, detail="Test prefatto group not found")
    if test_prefatto.generated:
        raise HTTPException(status_code=400, detail="Test prefatto group already triggered")
    if associated_testgroup:
        associated_tests = db.query(Test).filter(Test.testgroup_id == associated_testgroup.id).all()
        for test in associated_tests:
            db.delete(test)
        db.delete(associated_testgroup)
    db.commit()
    # Delete the test prefatto group
    test_prefatto = db.query(TestPrefattiGroup).filter(TestPrefattiGroup.id == id_testgroup_prefatto).first()
    if test_prefatto:
        db.delete(test_prefatto)

    # Commit the changes to the database
    db.commit()

    return {"Success": "Test prefatto group and associated tests deleted successfully"}
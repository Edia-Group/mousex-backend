from fastapi import APIRouter, Depends
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

    return {"message": "triggered \n TODO HAHAHAH"}


@testprefattigroup_router.get("/associated_test/{id_testgroup_prefatto}" ,response_model= List[TestBase] )
def read_tests_group(id_testgroup_prefatto : str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    user = get_username_from_token(token, db)
    associated_testgroup = db.query(TestsGroup).filter(TestsGroup.testprefattigroup_id == id_testgroup_prefatto).first()
    associated_test = db.query(Test).filter(Test.testgroup_id == associated_testgroup.id).all()

    return associated_test
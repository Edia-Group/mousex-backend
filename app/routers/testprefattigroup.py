from fastapi import APIRouter, Depends
from app.schemas.testprefattigroup import TestPrefattiGroupBase
from app.core.security import oauth2_scheme
from sqlalchemy.orm import Session
from app.core.database import get_db
from typing import List
from app.models.testPrefattGroup import TestPrefattiGroup

testprefattigroup_router = APIRouter(
    prefix="/testprefattigroup",
    tags=["TestPrefatti"], 
    responses={404: {"description": "Not found"}},
    )

@testprefattigroup_router.get("/all", response_model= List[TestPrefattiGroupBase] )
def read_tests_group(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    return db.query(TestPrefattiGroup).all()


@testprefattigroup_router.get("/create/{nome_testgroup_prefatto}", response_model= TestPrefattiGroupBase )
def read_tests_group(nome_testgroup_prefatto : str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    new_testprefattogroup =  TestPrefattiGroup.create(nome_testgroup_prefatto, db)
    return new_testprefattogroup

@testprefattigroup_router.get("/change_visibility/{id_testgroup_prefatto}", response_model= TestPrefattiGroupBase )
def read_tests_group(id_testgroup_prefatto : str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    return TestPrefattiGroup.change_visibility(id_testgroup_prefatto, db)

@testprefattigroup_router.get("/trigger/{id_testgroup_prefatto}")
def read_tests_group(id_testgroup_prefatto : str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    return {"message": "triggered \n TODO HAHAHAH"}



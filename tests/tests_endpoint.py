from fastapi import APIRouter, Depends, HTTPException, status
from models import Test
from security import oauth2_scheme
from sqlalchemy.orm import Session
from database import get_db
from autentication.auth_utils import get_username_from_token
from tests.tests_schemas import TestResponse
from tests.tests_util import get_random_domande_variante
from schemas import DomandaRisposta
test_router = APIRouter(
    prefix="/test", 
    tags=["Test"],   
    responses={404: {"description": "Not found"}},
    )


@test_router.get("/save/{id_test}", response_model=TestResponse)
def read_tests_group(id_test: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_username_from_token(token, db)
    test = db.query(Test).filter(Test.idTest == id_test, Test.utente_id == user.id).first()
    if not test.is_validate:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Test not validate")
    test.save(db)
    return test

@test_router.get("/validate/{id_test}", response_model=TestResponse)
def read_tests_group(id_test: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_username_from_token(token, db)
    test = db.query(Test).filter(Test.idTest == id_test, Test.utente_id == user.id).first()
    test.validate(db)
    return test

@test_router.get("/create", response_model=DomandaRisposta)
def read_tests_group(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_username_from_token(token, db)
    new_test = Test.create(user.id, db)
    domande = get_random_domande_variante(db)
    return {"domande":domande, "test_id" : new_test.idTest ,"dataOraInizio" : new_test.dataOraInizio}

@test_router.get("/{idTest}", response_model=TestResponse)
def read_tests_group(idTest: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_username_from_token(token, db)

    return db.query(Test).filter(Test.idTest == idTest, Test.utente_id == user.id).first()

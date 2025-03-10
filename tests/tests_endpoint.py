from fastapi import APIRouter, Depends
from testgroups.testgroups_schemas import TestsGroupWithUser, TestsGroupDelete
from models import Test
from security import oauth2_scheme
from sqlalchemy.orm import Session
from sqlalchemy import func as sqlfunc, select, and_
from models import Domanda, Variante
from database import get_db
from typing import List
from autentication.auth_utils import get_username_from_token
import random

test_router = APIRouter(
    prefix="/test", 
    tags=["Test"],   
    responses={404: {"description": "Not found"}},
    )

@test_router.get("/create_random")
def get_random_domande_variante(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
    username, id = get_username_from_token(token, db)

    rand_limit_domande = random.randint(13,18)
    domande = (
        db.query(Domanda)
        .order_by(sqlfunc.random())
        .limit(rand_limit_domande)
        .all()
    )

    domanda_ids = [domanda.idDomanda for domanda in domande]
    varianti = db.query(Variante).filter(Variante.domanda_id.in_(domanda_ids)).all()
    varianti_grouped = {}
    for variante in varianti:
        if variante.domanda_id not in varianti_grouped:
            varianti_grouped[variante.domanda_id] = []
        varianti_grouped[variante.domanda_id].append(variante)
    result_dict = {}
    for domanda in domande:
        if domanda.idDomanda in varianti_grouped.keys():
            result_dict[domanda.corpo] = [random.choice(varianti_grouped[domanda.idDomanda]), domanda.tipo]
    return result_dict


@test_router.get("/save/{id_test}")
def read_tests_group(id_test : int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    username, id = get_username_from_token(token, db)
    test = db.query(Test).filter(Test.idTest == id_test, Test.utente_id == id).first()
    test.save(db)
    return test

@test_router.get("/create")
def read_tests_group(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    username, id = get_username_from_token(token, db)
    new_test = Test.create(id, db)
    return new_test
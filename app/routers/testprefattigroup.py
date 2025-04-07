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
from app.models.testAdmin import TestAdmin
from app.schemas.test import TestBase
from app.models.user import User
from app.models.domanda import Domanda
from app.models.variante import Variante
from sqlalchemy import select
from app.schemas.domande import DomandaRisposta, DomandaOptions, DomandaRispostaPrewiew
import pytz
testprefattigroup_router = APIRouter(
    prefix="/testprefattigroup",
    tags=["TestPrefattiGroup"], 
    responses={404: {"description": "Not found"}},
    )

@testprefattigroup_router.get("/all", response_model= List[TestPrefattiGroupBase] )
def read_tests_group(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    return db.query(TestPrefattiGroup).filter(TestPrefattiGroup.is_deleted == False).all()

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
            data_ora_inserimento = datetime.now(pytz.timezone('Europe/Rome')),
            visibile = False,
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
            tipo=f"prefatto {str(test_prefatto.id)} triggered",
            utente_id=user.id,
            testprefattigroup_id=test_prefatto.id,
            data_ora_inserimento=datetime.now(pytz.timezone('Europe/Rome')),
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
    
    test_prefatto.is_deleted = True
    db.commit()
    db.refresh(test_prefatto)

    for test_group in associated_testgroup:
        test_group.visibile = False
        db.commit()
        db.refresh(test_group)

    return {"Success": "Test prefatto group and associated tests deleted successfully"}

@testprefattigroup_router.get("/test/{id_testgroup}", response_model= DomandaRisposta)
def read_tests_group(id_testgroup : str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    user = get_username_from_token(token, db)

    user_testgroup = db.query(TestsGroup).filter(TestsGroup.id == id_testgroup).first()
    if not user_testgroup:
        raise HTTPException(status_code=404, detail="Test group not found")
    if user_testgroup.nr_test <= 0:
        raise HTTPException(status_code=400, detail="No tests available for this group")
    id_prefatto = int(user_testgroup.tipo.split(" ")[1])
    test_prefatto = db.query(TestPrefattiGroup).filter(TestPrefattiGroup.id == id_prefatto).first()
    associated_testgroup = db.query(TestsGroup).filter(TestsGroup.testprefattigroup_id == id_prefatto,
                                                       TestsGroup.tipo == 'prefatto').first()
    if not test_prefatto:
        raise HTTPException(status_code=404, detail="Test prefatto group not found")
    tests_to_display = db.query(Test).filter(Test.testgroup_id == associated_testgroup.id, Test.contatore == user_testgroup.nr_test -1).first()
    if not associated_testgroup:
        raise HTTPException(status_code=404, detail="Associated test group not found")
    if not tests_to_display:
        raise HTTPException(status_code=404, detail="No tests to display . . .")
    
    user_testgroup.nr_test -= 1
    db.commit()
    db.refresh(user_testgroup)
    
    created_test = Test.create(
        id=user.id, 
        secondi_ritardo=associated_testgroup.secondi_ritardo,
        tipo=user_testgroup.tipo,
        db=db,
        contatore=tests_to_display.contatore,
        testgroup_id=user_testgroup.id
    )

    domande_list = (
        db.query(Domanda)
        .join(TestAdmin, Domanda.id_domanda == TestAdmin.id_domanda)
        .filter(TestAdmin.id_test == tests_to_display.id_test)
        .all()
    )

    varianti = db.execute(
        select(Domanda, Variante)
        .join(Variante, Domanda.id_domanda == Variante.domanda_id)
    ).all()

    grouped_varianti = {}
    for domanda, variante in varianti:
        if domanda.id_domanda not in grouped_varianti:
            grouped_varianti[domanda.id_domanda] = {"domanda": domanda, "varianti": []}
        grouped_varianti[domanda.id_domanda]["varianti"].append(variante.corpo)
    domande_returned = []
    print(grouped_varianti)
    domande_list_sorted = sorted(domande_list, key=lambda domanda: (domanda.numero_pagina, domanda.posizione))
    for domanda in domande_list_sorted:
        domande_returned.append(
            DomandaOptions(
                domanda=domanda,
                varianti=grouped_varianti[domanda.id_domanda]["varianti"],
        ))

    return DomandaRisposta(
        domande=domande_returned,
        test_id=created_test.id_test,
        data_ora_inizio=created_test.data_ora_inizio,
        show_riepilogo=tests_to_display.show_riepilogo,
    )

@testprefattigroup_router.get("/test/{id_testgroup}/preview", response_model= DomandaRispostaPrewiew)
def read_tests_group(id_testgroup : str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    user = get_username_from_token(token, db)

    user_testgroup = db.query(TestsGroup).filter(TestsGroup.id == id_testgroup).first()
    if not user_testgroup:
        raise HTTPException(status_code=404, detail="Test group not found")
    if user_testgroup.nr_test <= 0:
        raise HTTPException(status_code=400, detail="No tests available for this group")
    id_prefatto = int(user_testgroup.tipo.split(" ")[1])
    test_prefatto = db.query(TestPrefattiGroup).filter(TestPrefattiGroup.id == id_prefatto).first()
    associated_testgroup = db.query(TestsGroup).filter(TestsGroup.testprefattigroup_id == id_prefatto,
                                                       TestsGroup.tipo == 'prefatto').first()
    if not test_prefatto:
        raise HTTPException(status_code=404, detail="Test prefatto group not found")
    tests_to_display = db.query(Test).filter(Test.testgroup_id == associated_testgroup.id, Test.contatore == user_testgroup.nr_test -1).first()
    if not associated_testgroup:
        raise HTTPException(status_code=404, detail="Associated test group not found")
    if not tests_to_display:
        raise HTTPException(status_code=404, detail="No tests to display . . .")
    

    domande_list = (
        db.query(Domanda)
        .join(TestAdmin, Domanda.id_domanda == TestAdmin.id_domanda)
        .filter(TestAdmin.id_test == tests_to_display.id_test)
        .all()
    )

    varianti = db.execute(
        select(Domanda, Variante)
        .join(Variante, Domanda.id_domanda == Variante.domanda_id)
    ).all()

    grouped_varianti = {}
    for domanda, variante in varianti:
        if domanda.id_domanda not in grouped_varianti:
            grouped_varianti[domanda.id_domanda] = {"domanda": domanda, "varianti": []}
        grouped_varianti[domanda.id_domanda]["varianti"].append(variante.corpo)
    domande_returned = []
    print(grouped_varianti)
    domande_list_sorted = sorted(domande_list, key=lambda domanda: (domanda.numero_pagina, domanda.posizione))
    for domanda in domande_list_sorted:
        domande_returned.append(
            DomandaOptions(
                domanda=domanda,
                varianti=grouped_varianti[domanda.id_domanda]["varianti"],
        ))

    return DomandaRispostaPrewiew(
        domande=domande_returned,
    )
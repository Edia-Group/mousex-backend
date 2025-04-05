from fastapi import APIRouter, Depends, HTTPException
from app.models.test import Test
from app.core.security import oauth2_scheme
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.auth import get_username_from_token
from app.schemas.test import TestResponse
from app.models.testPrefattGroup import TestPrefattiGroup
from app.utils.user import get_random_domande_variante
from app.schemas.domande import DomandaRisposta, DomandaOptions, DomandaRispostaPrewiew
from app.schemas.test import TestCreateRequest, FormattedTest
from app.models.domanda import Domanda
from app.models.variante import Variante
from app.models.testAdmin import TestAdmin
from app.models.test import Test
from app.models.user import User
from sqlalchemy import text, select
from app.utils.test import generate_distinct_variations
import logging
from typing import List
from datetime import datetime, timedelta
from app.schemas.test import TestBase
from app.models.testgroup import TestsGroup
import pytz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

test_router = APIRouter(
    prefix="/test", 
    tags=["Test"],   
    responses={404: {"description": "Not found"}},
    )

@test_router.get("/validate/{id_test}", response_model=TestResponse)
def read_tests_group(id_test: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_username_from_token(token, db)
    test = db.query(Test).filter(Test.id_test == id_test, Test.utente_id == user.id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    test.validate(db)
    return test

@test_router.post("/create", response_model=DomandaRisposta)
def create_test(
    request_data: TestCreateRequest,
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    user = get_username_from_token(token, db)
    
    secondi_ritardo = request_data.secondi_ritardo
        
    new_test = Test.create(
        id=user.id, 
        secondi_ritardo=secondi_ritardo,
        tipo=request_data.tipo,
        db=db
    )

    domande_with_options = []
    domande_with_varianti = db.query(Variante).all()
    ids_domande = [domanda.domanda_id for domanda in domande_with_varianti]
    domande = get_random_domande_variante(db)
    for domanda in domande:
        if domanda.id_domanda in ids_domande:
            opzioni = sorted(
                [(variante.corpo, variante.posizione) for variante in domande_with_varianti if variante.domanda_id == domanda.id_domanda],
                key=lambda variante: variante[1]
            )
            opzioni = [variante[0] for variante in opzioni]
        else:
            opzioni = generate_distinct_variations(domanda.risposta_esatta)
        domande_with_options.append(
            DomandaOptions(
                domanda=domanda,
                varianti=opzioni
            )
        )
        
    return DomandaRisposta(
        domande=domande_with_options, test_id=new_test.id_test, data_ora_inizio=new_test.data_ora_inizio
    ) 

@test_router.get("/{idTest}", response_model=TestResponse)
def read_tests_group(idTest: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_username_from_token(token, db)

    return db.query(Test).filter(Test.idTest == idTest, Test.utente_id == user.id).first()

@test_router.delete("/delete/{idTest}", response_model=TestResponse)
def read_tests_group(idTest: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_username_from_token(token, db)

    test_delete =  db.query(Test).filter(Test.id_test == idTest, Test.utente_id == user.id).first()
    if not test_delete:
        raise HTTPException(status_code=404, detail="Test not found")
    
    associated_question = db.query(TestAdmin).filter(TestAdmin.id_test == idTest).all()
    if associated_question:
        for question in associated_question:
            db.delete(question)
        db.commit()

    db.delete(test_delete)
    db.commit()
    return test_delete

@test_router.delete("/delete/{idTest}/prefatto/{id_testprefatto}", response_model=TestResponse)
def read_tests_group(idTest: int, id_testprefatto: int,token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_username_from_token(token, db)

    prefatto_associated = db.query(TestPrefattiGroup).filter(TestPrefattiGroup.id == id_testprefatto).first()
    if not prefatto_associated:
        raise HTTPException(status_code=404, detail="TestGroup not found")
    testgroup_associated = db.query(TestsGroup).filter(TestsGroup.testprefattigroup_id == id_testprefatto).first()
    if not testgroup_associated:
        raise HTTPException(status_code=404, detail="TestGroup not found")
    
    all_tests_associated = db.query(Test).filter(Test.testgroup_id == testgroup_associated.id).all()
    test_delete =  db.query(Test).filter(Test.id_test == idTest).first()
    if not test_delete:
        raise HTTPException(status_code=404, detail="Test not found")
    
    for test in all_tests_associated:
        if test.contatore > test_delete.contatore:
            test.contatore -= 1
            db.commit()
            db.refresh(test)
    
    associated_question = db.query(TestAdmin).filter(TestAdmin.id_test == idTest).all()
    if associated_question:
        for question in associated_question:
            db.delete(question)
        db.commit()

    db.delete(test_delete)
    db.commit()
    testgroup_associated.nr_test -= 1
    db.commit()
    db.refresh(testgroup_associated)

    return test_delete

@test_router.post("/admin-test")
async def create_domande(formattedTest: FormattedTest, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    try:
        user = get_username_from_token(token, db)

        domanda_varianti_map = {}
        domande_data = []

        for pagine_number, pagina in formattedTest.formattedTest.items():
            for posizione, domanda in enumerate(pagina.domanda):
                print(pagine_number)
                new_domanda = Domanda(
                    corpo=domanda.corpo,
                    risposta_esatta=domanda.risposta_esatta,
                    tipo=domanda.tipo,
                    numero_pagina=int(pagine_number.strip("pagina")),
                    posizione=posizione
                )
                domande_data.append(new_domanda)

                varianti_data = []
                for i, variante in enumerate(domanda.opzioni):
                    new_variante = Variante(
                        corpo=variante,
                        tipo=domanda.tipo,
                        numero_pagina=int(pagine_number.strip("pagina")),
                        posizione=i
                    )
                    varianti_data.append(new_variante)

                domanda_varianti_map[new_domanda] = varianti_data

        # Manual INSERTs with returning clause
        inserted_ids = []
        for domanda in domande_data:
            insert_stmt = text(
                "INSERT INTO domande (corpo, risposta_esatta, tipo, numero_pagina, attivo, posizione) "
                "VALUES (:corpo, :risposta_esatta, :tipo, :numero_pagina, :attivo, :posizione) "
                "RETURNING id_domanda"
            )
            result = db.execute(
                insert_stmt,
                {
                    "corpo": domanda.corpo,
                    "risposta_esatta": domanda.risposta_esatta,
                    "tipo": domanda.tipo,
                    "numero_pagina": domanda.numero_pagina,
                    "attivo": True,
                    "posizione": domanda.posizione
                },
            )
            inserted_ids.append(result.scalar())

        # Update Domanda objects with generated IDs
        for i, domanda in enumerate(domande_data):
            domanda.id_domanda = inserted_ids[i]

        # Rest of your code (Varianti, Test, TestAdmin)
        varianti_to_insert = []
        for domanda, varianti in domanda_varianti_map.items():
            for variante in varianti:
                variante.domanda_id = domanda.id_domanda
                varianti_to_insert.append(variante)

        db.bulk_save_objects(varianti_to_insert)
        db.commit()
        if formattedTest.data_ora_inizio:
            print(formattedTest.data_ora_inizio)
            new_test = Test.create_collettivo(
                id=user.id,
                secondi_ritardo=5,
                tipo= 'collettivo',
                db=db,
                data_ora_inizo=formattedTest.data_ora_inizio - timedelta(hours=2),
            )
        else:
            id_testgroupprefatto = formattedTest.id_testgroup_prefatto
            testgroup_associated = db.query(TestsGroup).filter(TestsGroup.testprefattigroup_id == id_testgroupprefatto).first()
            new_test = Test.create(
                id=user.id,
                secondi_ritardo=5,
                tipo= 'prefatto',
                db=db,
                contatore = testgroup_associated.nr_test,
                testgroup_id = testgroup_associated.id
            )
            testgroup_associated.nr_test += 1
            db.commit()
            db.refresh(testgroup_associated)
            
        test_admin_data = [
            TestAdmin(
                id_test=new_test.id_test,
                id_domanda=domanda_id
            )
            for domanda_id in inserted_ids
        ]
        print(formattedTest.data_ora_inizio, "formattedTest.data_ora_inizio")

        db.bulk_save_objects(test_admin_data)
        db.commit()

        return formattedTest
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
    
@test_router.get("/test_collettivo/{id_testcollettivo}", response_model= DomandaRisposta)
def read_tests_group(id_testcollettivo : str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    user = get_username_from_token(token, db)

    tests_to_display = db.query(Test).filter(Test.id_test == id_testcollettivo).first()

    if not tests_to_display:
        raise HTTPException(status_code=404, detail="No test to display")
    
    created_test = Test.create_collettivo(
        id=user.id, 
        secondi_ritardo=0,
        tipo="collettivo" + " " + str(tests_to_display.id_test),
        db=db,
        contatore=tests_to_display.contatore,
        data_ora_inizo=tests_to_display.data_ora_inizio,
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
        data_ora_inizio=tests_to_display.data_ora_inizio,
    )

@test_router.get("/test_collettivi/all", response_model= List[TestBase])
def read_tests_group(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    user = get_username_from_token(token, db)
    tests_collettivi = db.query(Test).filter(Test.tipo == 'collettivo',
                                             Test.is_active == True,
                                             ).all()

    return tests_collettivi

@test_router.get("/test_collettivi/me", response_model= List[TestBase])
def read_tests_group(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    user = get_username_from_token(token, db)
    tests_collettivi = db.query(Test).filter(Test.tipo == 'collettivo',
                                             Test.generated == True,
                                             Test.is_active == True,
                                             Test.data_ora_inizio > datetime.now(pytz.timezone('Europe/Rome')),
                                             ).all()

    return tests_collettivi

@test_router.delete("/test_collettivo/delete/{id_testcollettivo}", response_model= TestBase)
def delete_tests_group(id_testcollettivo : str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    user = get_username_from_token(token, db)
    to_delete = db.query(Test).filter(Test.id_test == id_testcollettivo).first()
    if not to_delete:
        raise HTTPException(status_code=404, detail="Test not found")
    to_delete.is_active = False
    db.commit()
    db.refresh(to_delete)

    return to_delete

@test_router.get("/test_collettivi/{id_testcollettivo}/toggle", response_model= TestBase)
def toggle_test_collettivo(id_testcollettivo : str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    user = get_username_from_token(token, db)
    to_toggle = db.query(Test).filter(Test.id_test == id_testcollettivo).first()
    to_toggle.generated = not to_toggle.generated   
    db.commit()
    db.refresh(to_toggle)

    return to_toggle

@test_router.get("/test_collettivo/{id_test}/preview", response_model= DomandaRispostaPrewiew)
def read_tests_group(id_test : str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):


    tests_to_display = db.query(Test).filter(Test.id_test == id_test).first()

    if not tests_to_display:
        raise HTTPException(status_code=404, detail="No test to display")

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

    domande_list_sorted = sorted(domande_list, key=lambda domanda: (domanda.numero_pagina, domanda.posizione))
    print(domande_list_sorted)
    for domanda in domande_list_sorted:
        domande_returned.append(
            DomandaOptions(
                domanda=domanda,
                varianti=grouped_varianti[domanda.id_domanda]["varianti"],
        ))
    return DomandaRispostaPrewiew(
        domande=domande_returned,
    )
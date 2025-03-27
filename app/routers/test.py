from fastapi import APIRouter, Depends, HTTPException, status
from app.models.test import Test
from app.core.security import oauth2_scheme
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.auth import get_username_from_token
from app.schemas.test import TestResponse
from app.utils.user import get_random_domande_variante
from app.schemas.domande import DomandaRisposta, DomandaOptions
from app.schemas.test import TestCreateRequest, FormattedTest
from app.models.domanda import Domanda
from app.models.variante import Variante
from app.models.testAdmin import TestAdmin
from app.models.test import Test
from sqlalchemy import text
from app.utils.test import generate_distinct_variations
import logging
from app.models.testgroup import TestsGroup

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
    domande = get_random_domande_variante(db)
    for domanda in domande:
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

@test_router.post("/admin-test")
async def create_domande(formattedTest: FormattedTest, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    try:
        user = get_username_from_token(token, db)

        domanda_varianti_map = {}
        domande_data = []

        for pagine_number, pagina in formattedTest.formattedTest.items():
            for posizione, domanda in enumerate(pagina.domanda):
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
            new_test = Test.create(
                id=user.id,
                secondi_ritardo=5,
                tipo= 'collettivo',
                db=db,
            )
        else:
            id_testgroupprefatto = formattedTest.nome_prefatto
            testgroup_associated = db.query(TestsGroup).filter(TestsGroup.id == id_testgroupprefatto).first()
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
        

        db.bulk_save_objects(test_admin_data)
        db.commit()

        return formattedTest
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
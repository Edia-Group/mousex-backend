from fastapi import APIRouter, Depends, HTTPException, status
from app.models.test import Test
from app.core.security import oauth2_scheme
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.auth import get_username_from_token
from app.schemas.test import TestResponse
from app.utils.user import get_random_domande_variante
from app.schemas.domande import DomandaRisposta
from app.schemas.test import TestCreateRequest, DomandePagine

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

@test_router.post("/create", response_model=DomandaRisposta)
def create_test(
    request_data: TestCreateRequest,
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    user = get_username_from_token(token, db)
    
    # Get seconds delay either from request
    secondi_ritardo = request_data.secondi_ritardo
        
    new_test = Test.create(
        id=user.id, 
        secondi_ritardo=secondi_ritardo,
        tipo=request_data.tipo,
        db=db
    )
    
    domande = get_random_domande_variante(db)
    return DomandaRisposta(
        domande=domande, test_id=new_test.id_test, data_ora_inizio=new_test.data_ora_inizio
    ) 

@test_router.get("/{idTest}", response_model=TestResponse)
def read_tests_group(idTest: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_username_from_token(token, db)

    return db.query(Test).filter(Test.idTest == idTest, Test.utente_id == user.id).first()

@test_router.post("/admin-test")
async def create_domande(domande: DomandePagine):
    print(domande.model_dump())
    return {"pagine" : domande.__dict__}

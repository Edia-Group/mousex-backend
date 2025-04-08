from fastapi import APIRouter, Depends
from app.models.domanda import Domanda as DomandaModel
from app.schemas.domande import DomandaResponse, Domanda
from app.core.security import oauth2_scheme
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.domande import FormattedQuestions
from app.utils.auth import get_username_from_token
from typing import List
from app.models.variante import Variante
from app.models.testAdmin import TestAdmin

domande_router = APIRouter(
    prefix="/domande", 
    tags=["Domande"],   
    responses={404: {"description": "Not found"}},
    )

@domande_router.post("/create_basic_import", response_model=DomandaResponse)
def create_domanda(
    domande: List[Domanda],
    db: Session = Depends(get_db)
):        
    new_domande = [DomandaModel(
        corpo=domanda.corpo,
        tipo=domanda.tipo,
        risposta_esatta=domanda.risposta_esatta,
    )for domanda in domande]
    db.bulk_save_objects(new_domande)
    db.commit()
    return domande

@domande_router.post("/create")
def create_test(
    request_data: FormattedQuestions,
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):        
    user = get_username_from_token(token, db)
    base_question = request_data.formattedQuestions
    new_questions = [
        DomandaModel(
            corpo=base_question.corpo + " " + variante.variante_corpo,
            tipo=base_question.tipo,
            risposta_esatta=variante.variante_risposta_corretta,
        )
        for variante in base_question.varianti
    ]
    db.bulk_save_objects(new_questions)
    db.commit()

    return request_data

@domande_router.get("/all", response_model=List[DomandaResponse])
def create_test(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):        
    user = get_username_from_token(token, db)

    return db.query(DomandaModel).filter(DomandaModel.attivo == True).all()

@domande_router.put("/modify/{id_domanda}", response_model=DomandaResponse)
def modify_domanda(
    id_domanda: int,
    new_domanda: DomandaResponse,
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):        
    user = get_username_from_token(token, db)
    domanda = db.query(DomandaModel).filter(DomandaModel.id_domanda == id_domanda).first()
    
    if not domanda:
        return {"error": "Domanda not found"}
    
    for key, value in new_domanda.model_dump().items():
        setattr(domanda, key, value)
    
    db.commit()
    db.refresh(domanda)
    return domanda

@domande_router.delete("/delete/{id_domanda}")
def delete_domanda(
    id_domanda: int,
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):        
    user = get_username_from_token(token, db)
    domanda = db.query(DomandaModel).filter(DomandaModel.id_domanda == id_domanda).first()
    if not domanda:
        return {"error": "Domanda not found"}
    
    db.query(Variante).filter(Variante.domanda_id == id_domanda).delete(synchronize_session=False)
    db.query(TestAdmin).filter(TestAdmin.id_domanda == id_domanda).delete(synchronize_session=False)
    db.delete(domanda)
    db.commit()
    return {"message": "Domanda and its varianti deleted"}

from fastapi import APIRouter, Depends
from app.models.domanda import Domanda as DomandaModel
from app.schemas.domande import DomandaResponse, Domanda
from app.core.security import oauth2_scheme
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.domande import FormattedQuestions
from app.utils.auth import get_username_from_token
from typing import List

domande_router = APIRouter(
    prefix="/domande", 
    tags=["Domande"],   
    responses={404: {"description": "Not found"}},
    )


@domande_router.post("/create")
def create_test(
    request_data: FormattedQuestions,
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):        
    user = get_username_from_token(token, db)
    new_questions = [
        Domanda(
            corpo=formatted_question.corpo + " " + variante.variante_corpo,
            tipo=formatted_question.tipo,
            risposta_esatta=variante.variante_risposta_corretta,
        )
        for formatted_question in request_data.formattedQuestions
        for variante in formatted_question.varianti
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

    return db.query(DomandaModel).all()

@domande_router.put("/modify/{id_domanda}", response_model=DomandaResponse)
def modify_domanda(
    id_domanda: int,
    new_domanda: Domanda,
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):        
    user = get_username_from_token(token, db)
    domanda = db.query(DomandaModel).filter(DomandaModel.id == id_domanda).first()
    
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
    domanda = db.query(DomandaModel).filter(DomandaModel.id == id_domanda).first()
    
    if not domanda:
        return {"error": "Domanda not found"}
    
    db.delete(domanda)
    db.commit()
    return {"message": "Domanda deleted"}
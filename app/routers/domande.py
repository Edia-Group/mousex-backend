from fastapi import APIRouter, Depends
from app.models.domanda import Domanda
from app.core.security import oauth2_scheme
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.domande import FormattedQuestions
from app.utils.auth import get_username_from_token

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

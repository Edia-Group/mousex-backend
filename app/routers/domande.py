from fastapi import APIRouter, Depends
from app.models.domanda import Domanda
from app.core.security import oauth2_scheme
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.auth import get_username_from_token
from app.utils.user import get_random_domande_variante
from app.schemas.domande import DomandaRisposta
from app.schemas.domande import DomandaCreate, DomandaResponse

domande_router = APIRouter(
    prefix="/domande", 
    tags=["Domande"],   
    responses={404: {"description": "Not found"}},
    )


@domande_router.post("/create", response_model=DomandaResponse)
def create_test(
    request_data: DomandaCreate,
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    user = get_username_from_token(token, db)
        
    new_domanda = Domanda.create(
        Domanda(
            **request_data.model_dump(),
        ),
        db
    )
    return new_domanda

from fastapi import APIRouter, Depends
from app.models.domanda import Domanda
from app.core.security import oauth2_scheme
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.domande import DomandaCreate, DomandeList

domande_router = APIRouter(
    prefix="/domande", 
    tags=["Domande"],   
    responses={404: {"description": "Not found"}},
    )


@domande_router.post("/create")
def create_test(
    request_data: DomandeList,
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):        
    for domande in request_data.domande:
        print(domande)

    return request_data

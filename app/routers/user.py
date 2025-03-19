from fastapi import APIRouter, Depends
from app.core.security import oauth2_scheme
from sqlalchemy.orm import Session
from app.core.database import get_db
from sqlalchemy import func, extract, desc
from app.utils.auth import get_username_from_token
from datetime import datetime, timedelta
from app.schemas.user import UserStats, UserTests, TestSchema
from app.models.statistiche import Statistiche
from app.models.test import Test

users_router = APIRouter(
    prefix="/users", 
    tags=["Users"],   
    responses={404: {"description": "Not found"}},
    )

@users_router.get("/me")
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return get_username_from_token(token, db)
    

@users_router.get("/stats", response_model = UserStats)
async def read_user_stats(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_username_from_token(token, db)

    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    stella_stats = db.query(Statistiche).filter(Statistiche.utente_id == user.id, Statistiche.tipo_domanda == 'stelle').first()

    test_count = db.query(func.count(Test.id_test)).filter(
        Test.utente_id == user.id,
        func.date(Test.data_ora_fine) >= start_of_week,
        func.date(Test.data_ora_fine) <= end_of_week,
    ).scalar() or 0

    stelle_count = stella_stats.nr_errori if stella_stats else 0

    return UserStats(
        username=user.username,
        stelle=stelle_count,
        test_settimanali=test_count,
    )

@users_router.get("/last_tests", response_model=UserTests)
async def get_last_tests(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_username_from_token(token, db)

    last_tests = db.query(Test).filter(Test.utente_id == user.id, Test.tempo_impiegato > 0).order_by(desc(Test.data_ora_inserimento)).limit(100).all()

    test_schemas = [TestSchema(
        idTest=test.idTest,
        dataOraInizio=test.data_ora_inizio,
        tipo=test.tipo,
        inSequenza=test.in_sequenza,
        nrGruppo=test.nr_gruppo,
        secondiRitardo=test.secondi_ritardo,
        utente_id=test.utente_id,
        dataOraFine=test.data_ora_fine,
        dataOraInserimento=test.data_ora_inserimento,
        nrTest=test.nr_test,
        malusF5=test.malus_f5,
        numeroErrori=test.numero_errori,
        tempo_impiegato = test.tempo_impiegato
    ) for test in last_tests]

    return UserTests(username=user.username, tests=test_schemas)
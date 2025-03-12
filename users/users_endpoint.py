from fastapi import APIRouter, Depends
from security import oauth2_scheme
from sqlalchemy.orm import Session
from database import get_db
from sqlalchemy import func, extract, desc
from autentication.auth_utils import get_username_from_token
from datetime import datetime, timedelta
from users.users_schemas import UserStats, UserTests, TestSchema
from models import Statistiche, Test

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

    test_count = db.query(func.count(Test.idTest)).filter(
        Test.utente_id == user.id,
        func.date(Test.dataOraFine) >= start_of_week,
        func.date(Test.dataOraFine) <= end_of_week,
    ).scalar() or 0

    return UserStats(
        username=user.username,
        stelle=stella_stats.nr_errori,
        test_settimanali=test_count,
    )

@users_router.get("/last_tests", response_model=UserTests)
async def get_last_tests(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_username_from_token(token, db)

    last_tests = db.query(Test).filter(Test.utente_id == user.id, Test.tempo_impiegato > 0).order_by(desc(Test.dataOraInserimento)).limit(100).all()

    test_schemas = [TestSchema(
        idTest=test.idTest,
        dataOraInizio=test.dataOraInizio,
        tipo=test.tipo,
        inSequenza=test.inSequenza,
        nrGruppo=test.nrGruppo,
        secondiRitardo=test.secondiRitardo,
        utente_id=test.utente_id,
        dataOraFine=test.dataOraFine,
        dataOraInserimento=test.dataOraInserimento,
        nrTest=test.nrTest,
        malusF5=test.malusF5,
        numeroErrori=test.numeroErrori,
        tempo_impiegato = test.tempo_impiegato
    ) for test in last_tests]

    return UserTests(username=user.username, tests=test_schemas)
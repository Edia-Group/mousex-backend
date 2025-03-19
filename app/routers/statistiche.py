from fastapi import APIRouter, Depends
from app.models.domanda import Domanda
from app.core.security import oauth2_scheme
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.statistiche import StatisticheStelle, StatisticheTestSettimanali
from app.utils.auth import get_username_from_token
from typing import List
from app.models.user import User
from app.models.statistiche import Statistiche
from app.models.test import Test
from app.schemas.statistiche import TestBaseStats
import csv
from fastapi.responses import StreamingResponse
from io import StringIO

statistiche_router = APIRouter(
    prefix="/statistiche", 
    tags=["Statistiche"],   
    responses={404: {"description": "Not found"}},
    )


@statistiche_router.get("/stelle", response_model=List[StatisticheStelle])
def create_test(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):        
    user = get_username_from_token(token, db)
    users = db.query(User).all()
    stelle = db.query(Statistiche).filter(Statistiche.tipo_domanda == "stelle").all()
    stats = sorted(
        [StatisticheStelle(utente=user, stelle=stella.nr_errori) for user, stella in zip(users, stelle) if stella.utente_id == user.id],
        key=lambda x: x.stelle
    )
    return stats
     
@statistiche_router.get("/test-settimanali", response_model=List[StatisticheTestSettimanali])
def create_test(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):        
    users = db.query(User).all()
    tests = db.query(Test).filter(Test.tipo == "manuale").all()

    stats = sorted(
        [StatisticheTestSettimanali(utente=user, test_settimanali=len([test for test in tests if test.utente_id == user.id]),
        media = sum([test.tempo_impiegato for test in tests if test.utente_id == user.id])/len([test for test in tests if test.utente_id == user.id])
        ) for user in users],
        key=lambda x: x.test_settimanali
    )
    return stats

@statistiche_router.get("/riepilogo", response_model=List[TestBaseStats])
def create_test(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):        
    users = db.query(User).all()
    tests = db.query(Test).all()
    return [TestBaseStats(Test=test, utente=user) for user in users for test in tests if test.utente_id == user.id]

@statistiche_router.get("/csv_riepilogo", response_model=List[TestBaseStats])
def create_test(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):        
    users = db.query(User).all()
    tests = db.query(Test).all()

    # Prepare CSV data
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Test ID", "User ID", "Tipo", "Tempo Impiegato"])  # Header row
    for test in tests:
        if test.tipo == "manuale":
            writer.writerow([test.id_test, test.utente_id, test.tipo, test.tempo_impiegato])
    output.seek(0)

    # Return CSV as a streaming response
    response = StreamingResponse(output, media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=tests_dump.csv"
    return response

@statistiche_router.get("/riepilogo", response_model=List[TestBaseStats])
def create_test(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):        
    users = db.query(User).all()
    tests = db.query(Test).all()
    return [TestBaseStats(Test=test, utente=user) for user in users for test in tests if test.utente_id == user.id]

@statistiche_router.get("/csv_riepilogo", response_model=List[TestBaseStats])
def create_test(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):        
    users = db.query(User).all()
    tests = db.query(Test).all()

    # Prepare CSV data
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Test ID", "User ID", "Tipo", "Tempo Impiegato"])  # Header row
    for test in tests:
        if test.tipo == "collettivo":
            writer.writerow([test.id_test, test.utente_id, test.tipo, test.tempo_impiegato])
    output.seek(0)

    # Return CSV as a streaming response
    response = StreamingResponse(output, media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=tests_dump.csv"
    return response
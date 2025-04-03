from fastapi import APIRouter, Depends, HTTPException, logger
from app.models.domanda import Domanda
from app.core.security import oauth2_scheme
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.statistiche import Statistiche_Page, StatisticheTestSettimanali, StatisticheBase
from app.utils.auth import get_username_from_token
from typing import List
from app.models.user import User
from app.models.statistiche import Statistiche
from app.models.test import Test
from app.schemas.statistiche import TestBaseStats
import csv
from app.models.testPrefattGroup import TestPrefattiGroup
from fastapi.responses import StreamingResponse
from io import StringIO

statistiche_router = APIRouter(
    prefix="/statistiche", 
    tags=["Statistiche"],   
    responses={404: {"description": "Not found"}},
    )

     
@statistiche_router.get("/test-settimanali", response_model=List[StatisticheTestSettimanali])
def create_test(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):        
    users = db.query(User).all()
    tests = db.query(Test).filter(Test.tempo_impiegato > 1).all()
    stats = []
    for user in users:
        user_tests = [test for test in tests if test.utente_id == user.id]
        test_count = len(user_tests)
        if test_count > 0:
            average_time = sum(test.tempo_impiegato for test in user_tests) / test_count
        else:
            average_time = 0
            
        stats.append(StatisticheTestSettimanali(
            utente=user,
            test_settimanali=test_count,
            media=average_time
        ))
    
    stats.sort(key=lambda x: x.test_settimanali)
    
    return stats



@statistiche_router.get("/riepilogo", response_model=List[TestBaseStats])
def create_test(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):        
    users = db.query(User).filter(User.is_superuser == False).all()
    tests = db.query(Test).all()
    return [TestBaseStats(Test=test, utente=user) for user in users for test in tests if test.utente_id == user.id]


@statistiche_router.get("/all", response_model=List[Statistiche_Page])
def get_all_statistiche(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):        
    user = get_username_from_token(token, db)
    stats = db.query(Statistiche).filter(Statistiche.utente_id == user.id).all()
    test_incompleti = db.query(Test).filter(Test.utente_id == user.id, Test.data_ora_fine == None).count()
    return [Statistiche_Page(statistiche=stats, test_incompleti=test_incompleti)]
    

@statistiche_router.get("/increment/{char_type}", response_model =StatisticheBase)
def get_all_statistiche(
    char_type: str,
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):        
    user = get_username_from_token(token, db)
    stats_to_incrememt = db.query(Statistiche).filter(Statistiche.utente_id == user.id, Statistiche.tipo_domanda == char_type).first()
    stats_to_incrememt.nr_errori += 1
    db.commit()
    db.refresh(stats_to_incrememt)

    return stats_to_incrememt




##### ESTRAZIONI CSV #####
@statistiche_router.get("/csv_riepilogo")
def download_csv_report(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        non_superuser_users = db.query(User).filter(User.is_superuser == False).all()
        non_superuser_ids = {user.id for user in non_superuser_users}
        
        tests = db.query(Test).filter(Test.utente_id.in_(non_superuser_ids)).all()
        users = {user.id: user for user in non_superuser_users}
        
        output = StringIO()
        writer = csv.writer(output, delimiter=";")
        
        writer.writerow([
            "ID Test", 
            "Username", 
            "Tipo", 
            "Data Inizio", 
            "Data Fine", 
            "Tempo Impiegato", 
            "Errori"
        ])
        
        for test in tests:
            username = users.get(test.utente_id).username if test.utente_id in users else "Unknown"
            writer.writerow([
                test.id_test,
                username,
                test.tipo,
                test.data_ora_inizio.strftime("%Y-%m-%d %H:%M:%S") if test.data_ora_inizio else "",
                test.data_ora_fine.strftime("%Y-%m-%d %H:%M:%S") if test.data_ora_fine else "",
                f"{test.tempo_impiegato:.2f}" if test.tempo_impiegato else "",
                test.numero_errori
            ])
        
        output.seek(0)
        
        response = StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv"
        )
        
        response.headers["Content-Disposition"] = "attachment; filename=riepilogo_test.csv"
        
        return response
        
    except Exception as e:
        logger.error(f"Errore generazione riepilogo test CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@statistiche_router.get("/csv_riepilogo_collettivi/{id_testcollettivo}")
def download_csv_report_collettivi(id_testcollettivo : int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        print('ciao')
        tests = db.query(Test, User.username).join(User, Test.utente_id == User.id)
        tests = tests.filter(Test.tipo == f'collettivo {str(id_testcollettivo)}').order_by(Test.tempo_impiegato.asc()).all()
        output = StringIO()
        writer = csv.writer(output, delimiter=';')
        
        writer.writerow([
            "ID Test", 
            "Username", 
            "Tipo", 
            "Data Inizio", 
            "Data Fine", 
            "Tempo Impiegato", 
            "Errori"
        ])
        
        for test, utente in tests:
            username = utente if utente else "Unknown"
            writer.writerow([
                test.id_test,
                username,
                test.tipo,
                test.data_ora_inizio.strftime("%Y-%m-%d %H:%M:%S") if test.data_ora_inizio else "",
                test.data_ora_fine.strftime("%Y-%m-%d %H:%M:%S") if test.data_ora_fine else "",
                f"{test.tempo_impiegato:.2f}" if test.tempo_impiegato else "",
                test.numero_errori
            ])
        
        output.seek(0)
        
        response = StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv"
        )
        
        response.headers["Content-Disposition"] = "attachment; filename=csv_riepilogo_collettivi.csv"
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


@statistiche_router.get("/csv_riepilogo_prefatti/{id_testprefatto}")
def download_csv_report_prefatti(id_testprefatto:str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        test_prefatto = db.query(TestPrefattiGroup).filter(TestPrefattiGroup.id == id_testprefatto).first()
        non_superuser_users = db.query(User).filter(User.is_superuser == False).all()
        non_superuser_ids = {user.id for user in non_superuser_users}
        
        tests = db.query(Test).filter(
            Test.tipo == f"prefatto {str(test_prefatto.id)} triggered",
            Test.utente_id.in_(non_superuser_ids)
        ).all()
        
        users = {user.id: user for user in non_superuser_users}
        
        output = StringIO()
        writer = csv.writer(output, delimiter=';')
        
        writer.writerow([
            "ID Test", 
            "Username", 
            "Tipo", 
            "Data Inizio", 
            "Data Fine", 
            "Tempo Impiegato", 
            "Errori"
        ])
        
        for test in tests:
            username = users.get(test.utente_id).username if test.utente_id in users else "Unknown"
            writer.writerow([
                test.id_test,
                username,
                test.tipo,
                test.data_ora_inizio.strftime("%Y-%m-%d %H:%M:%S") if test.data_ora_inizio else "",
                test.data_ora_fine.strftime("%Y-%m-%d %H:%M:%S") if test.data_ora_fine else "",
                f"{test.tempo_impiegato:.2f}" if test.tempo_impiegato else "",
                test.numero_errori
            ])
        
        output.seek(0)
        
        response = StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv"
        )
        
        response.headers["Content-Disposition"] = "attachment; filename=riepilogo_test_prefatti.csv"
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")
from pydantic import BaseModel
from typing import List
from app.schemas.user import User
from app.schemas.test import TestBase

class StatisticheStelle(BaseModel):
    utente : User
    stelle : int

class StatisticheTestSettimanali(BaseModel):
    utente : User
    test_settimanali : int
    media : float

class TestBaseStats(BaseModel):
    Test: TestBase
    utente: User

class StatisticheBase(BaseModel):
    tipo_domanda: str
    nr_errori: int
    utente_id: int
    id: int
    class Config:
        from_attributes = True

class Statistiche_Page(BaseModel):
    statistiche: List[StatisticheBase]  
    test_incompleti: int
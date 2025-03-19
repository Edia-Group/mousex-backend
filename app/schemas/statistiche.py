from pydantic import BaseModel, ValidationError
from datetime import datetime
from typing import Optional, Dict
from app.schemas.domande import Pagina
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
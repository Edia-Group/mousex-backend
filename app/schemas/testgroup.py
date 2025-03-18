from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from typing import Optional
from .user import User

class TestsGroupDelete(BaseModel):
    id : int

class TestsGroupDeleteAll(BaseModel):
    tipo : str

class TestsGroupBase(BaseModel):
    nr_test: int
    tipo: str
    secondi_ritardo: int
    data_ora_inserimento: datetime

class TestsGroupCreate(BaseModel):
    nr_test: int
    tipo: Optional[str] = 'standard'
    data_ora_inizio: Optional[datetime] = None
    secondi_ritardo: Optional[int] = 5

class TestsGroupUpdate(TestsGroupBase):
    pass

class TestsGroup(TestsGroupBase):
    id: int

    class Config:
        from_attributes = True

class TestsGroupWithUser(TestsGroup):
    utente: User
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from typing import Optional
from users.users_schemas import User

class TestsGroupDelete(BaseModel):
    id : int

class TestsGroupBase(BaseModel):
    nr_test: int

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
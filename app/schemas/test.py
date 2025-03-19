from pydantic import BaseModel, ValidationError
from datetime import datetime
from typing import Optional, Dict
from app.schemas.domande import Pagina

class TestBase(BaseModel):
    id_test: int
    data_ora_inizio: Optional[datetime] = None
    tipo: str = 'Normale'
    in_sequenza: bool = False
    nr_gruppo: int = 0
    secondi_ritardo: int = 5
    utente_id: int
    data_ora_fine: Optional[datetime] = None
    data_ora_inserimento: datetime
    nr_test: int = 0
    malus_f5: bool = False
    numero_errori: int = 0
    tempo_impiegato: float 
    is_validate: bool 

    class Config:
        from_attributes = True

class TestResponse(TestBase):
    pass

class TestCreate(BaseModel):
    utente_id: int


class TestCreateRequest(BaseModel):
    tipo: str
    secondi_ritardo: int = 5
    group_id: Optional[int] = None

class FormattedTest(BaseModel):
    formattedTest: Dict[str, Pagina]
    data_ora_inizio: Optional[datetime] = None
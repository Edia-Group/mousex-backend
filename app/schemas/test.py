from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, List

class TestBase(BaseModel):
    id_test: int
    data_ora_inizio: Optional[datetime] = None
    tipo: str = 'Normale'
    generated: Optional[bool]
    nr_gruppo: int = 0
    secondi_ritardo: int = 5
    utente_id: int
    data_ora_fine: Optional[datetime] = None
    data_ora_inserimento: datetime
    nr_test: int = 0
    malus_f5: bool = False
    numero_errori: int = 0
    tempo_impiegato: float 
    is_validate: Optional[bool] 
    is_active: Optional[bool]

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

class Domanda(BaseModel):
    corpo: str
    opzioni: List[str]
    risposta_esatta: str
    tipo: str


class Pagina(BaseModel):
    domanda: List[Domanda]

class FormattedTest(BaseModel):
    formattedTest: Dict[str, Pagina]
    data_ora_inizio: Optional[datetime] = None
    id_testgroup_prefatto: Optional[int] = None
    show_riepilogo: Optional[bool] = None

class FormattedTestResponse(BaseModel):
    formattedTest: Dict[str, Pagina]
    data_ora_inizio: Optional[datetime] = None
    id_testgroup_prefatto: Optional[int] = None
    id_test: int
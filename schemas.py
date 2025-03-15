from typing import Optional, Dict, List, Union
from datetime import datetime
from pydantic import BaseModel, RootModel
# User schema

class UserCreate(BaseModel):
    username: str
    password: str

class Variante(BaseModel):
    corpo: str
    idVariante: int
    numeroPagine: Optional[int]
    domanda_id: int
    rispostaEsatta: str
    tipo: Optional[str]
    data_ora_inserimento: datetime
    attivo: Optional[bool]

class DomandaVarianteResponse(BaseModel):
    variante: Variante
    tipo: str

class DomandaRisposta(BaseModel):
    domande: Dict[str, DomandaVarianteResponse]
    test_id : int
    dataOraInizio: datetime

class TestCreateRequest(BaseModel):
    tipo: str
    secondi_ritardo: int = 5
    group_id: Optional[int] = None
from .variante import VarianteQuestion
from typing import List, Dict
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Opzione(BaseModel):
    corpo: str

class Domanda(BaseModel):
    corpo: str
    opzioni: List[str]
    risposta_esatta: str
    tipo: str

class Pagina(BaseModel):
    domanda: List[Domanda]

class FormattedQuestion(BaseModel):
    corpo: str
    varianti: List[VarianteQuestion]
    tipo: str

class FormattedQuestions(BaseModel):
    formattedQuestions: List[FormattedQuestion]
    
class DomandaUpdate(BaseModel):
    corpo: Optional[str] = None
    tipo: Optional[str] = None
    numero_pagina: Optional[int] = None
    attivo: Optional[bool] = None
    risposta_esatta: Optional[str] = None

class DomandaResponse(BaseModel):
    id_domanda: int
    corpo: str
    data_ora_inserimento: datetime
    tipo: str
    numero_pagina: Optional[int]
    attivo: bool
    risposta_esatta: str

    class Config:
        from_attributes = True

class DomandaVarianteResponse(BaseModel):
    variante: VarianteQuestion
    tipo: str

class DomandaOptions(BaseModel):
    domanda : DomandaResponse
    varianti : List[str]

class DomandaRisposta(BaseModel):
    domande: List[DomandaOptions]
    test_id : int
    data_ora_inizio: datetime





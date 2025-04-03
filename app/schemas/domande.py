from .variante import VarianteQuestion
from typing import List, Dict
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Opzione(BaseModel):
    corpo: str

class DomandaTest(BaseModel):
    corpo: str
    opzioni: List[str]
    risposta_esatta: str
    tipo: str

class Domanda(BaseModel):
    corpo: str
    risposta_esatta: str
    tipo: str
    class Config:
        from_attributes = True

class Pagina(BaseModel):
    domanda: List[DomandaTest]

class FormattedQuestion(BaseModel):
    corpo: str
    varianti: List[VarianteQuestion]
    tipo: str

class FormattedQuestions(BaseModel):
    formattedQuestions: FormattedQuestion
    
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

class DomandaRispostaPrewiew(BaseModel):
    domande: List[DomandaOptions]



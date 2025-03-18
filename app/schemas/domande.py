from .variante import Variante
from typing import List, Dict
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DomandaCreate(BaseModel):
    corpo: str
    tipo: Optional[str] = 'select'
    numero_pagina: Optional[int] = None
    attivo: Optional[bool] = True
    risposta_esatta: str

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
    variante: Variante
    tipo: str

class DomandaRisposta(BaseModel):
    domande: List[DomandaResponse]
    test_id : int
    data_ora_inizio: datetime


class PaginaCreate(BaseModel):
    domande: List[DomandaCreate]

from pydantic import BaseModel
from typing import List, Literal

class Variante(BaseModel):
    variante_corpo: str
    variante_risposta_corretta: str

class Domanda(BaseModel):
    corpo: str
    varianti: List[Variante]
    tipo: Literal["m", "t"]

class DomandeList(BaseModel):
    domande: List[Domanda]


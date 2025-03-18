from typing import Dict
from datetime import datetime
from pydantic import BaseModel
from .variante import Variante

class DomandaVarianteResponse(BaseModel):
    variante: Variante
    tipo: str

class DomandaRisposta(BaseModel):
    domande: Dict[str, DomandaVarianteResponse]
    test_id : int
    dataOraInizio: datetime
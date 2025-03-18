
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class Variante(BaseModel):
    corpo: str
    idVariante: int
    numeroPagine: Optional[int]
    domanda_id: int
    rispostaEsatta: str
    tipo: Optional[str]
    data_ora_inserimento: datetime
    attivo: Optional[bool]
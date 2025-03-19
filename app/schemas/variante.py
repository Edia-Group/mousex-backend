
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class VarianteQuestion(BaseModel):
    variante_corpo: str
    variante_risposta_corretta: str

class Variante(BaseModel):
    corpo: str
    idVariante: int
    numeroPagine: Optional[int]
    domanda_id: int
    rispostaEsatta: str
    tipo: Optional[str]
    data_ora_inserimento: datetime
    attivo: Optional[bool]

class VarianteCreate(BaseModel):
    corpo: str
    rispostaEsatta: str
from datetime import datetime
from pydantic import BaseModel

class TestPrefattiGroupBase(BaseModel):
    id: int
    nome: str
    generated: bool
    visible: bool
    data_ora_inserimento: datetime


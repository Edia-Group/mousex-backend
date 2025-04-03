from pydantic import BaseModel, Field, SecretStr
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    username: str = Field(..., max_length=150, description="Username (unique)")
    is_superuser: bool = Field(False, description="Is user a superuser?")
    is_active: bool = Field(True, description="Is user active?")

class UserCreate(BaseModel):
    username: str = Field(..., max_length=150, description="Username (unique)")
    password: str = Field(..., min_length=8, description="User password (minimum 8 characters)")

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=150, description="Username (unique)")
    password: Optional[SecretStr] = Field(None, min_length=8, description="User password (minimum 8 characters)")
    is_superuser: Optional[bool] = Field(None, description="Is user a superuser?")
    is_active: Optional[bool] = Field(None, description="Is user active?")

class User(UserBase):
    id: int = Field(..., description="User ID")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    class Config:
        from_attributes = True

class UserRead(User):
    pass 

class UserStats(BaseModel):
    username: str
    media: float
    media_settimanale: float
    test_settimanali: int

class TestSchema(BaseModel):
    idTest: int
    dataOraInizio: datetime | None
    tipo: str
    generated: Optional[bool]
    nrGruppo: int
    secondiRitardo: int
    utente_id: int
    dataOraFine: datetime | None
    dataOraInserimento: datetime
    is_active: Optional[bool]
    numeroErrori: int
    tempo_impiegato: float

class UserTests(BaseModel):
    username: str
    tests: List[TestSchema]
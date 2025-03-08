from pydantic import BaseModel

# User schema

class UserCreate(BaseModel):
    username: str
    password: str
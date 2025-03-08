from pydantic import BaseModel

# User schema

class UserCreate(BaseModel):
    username: str
    full_name: str
    email: str
    password: str
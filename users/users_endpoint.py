from fastapi import APIRouter, Depends
from security import oauth2_scheme
from sqlalchemy.orm import Session
from database import get_db
from autentication.auth_utils import SECRET_KEY, ALGORITHM
from autentication.auth_utils import get_username_from_token

users_router = APIRouter(
    prefix="/users", 
    tags=["Users"],   
    responses={404: {"description": "Not found"}},
    )

@users_router.get("/me")
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username, id = get_username_from_token(token, db)
    return {"username" : username, "id" : id}


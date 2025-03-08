from fastapi import APIRouter, HTTPException, Depends, status
from security import oauth2_scheme
from sqlalchemy.orm import Session
from database import get_db
from autentication.auth_utils import SECRET_KEY, ALGORITHM
from models import User
import jwt

users_router = APIRouter(
    prefix="/users", 
    tags=["Users"],   
    responses={404: {"description": "Not found"}},
    )

@users_router.get("/me")
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return {"username": user.username}


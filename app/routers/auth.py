from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.auth import UserCreate
from sqlalchemy.orm import Session
from app.core.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from app.utils.auth import get_password_hash, create_access_token, verify_password
from app.models.user import User

auth_router = APIRouter(
    prefix="/auth", 
    tags=["Auth"],   
    responses={404: {"description": "Not found"}},
    )

@auth_router.post("/register")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    hashed_password = get_password_hash(user.password)
    new_user = User.create(user.username, hashed_password, db)
    access_token = create_access_token({"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.post("/login")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username not in DB")
    if not verify_password(user.password, existing_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong Password")
    
    access_token = create_access_token({"sub": existing_user.username})
    return {"access_token": access_token, "user" : existing_user}

@auth_router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
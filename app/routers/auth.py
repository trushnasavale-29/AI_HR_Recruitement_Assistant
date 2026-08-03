from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.database.database import get_db
from app.models.candidate import User
import hashlib

router = APIRouter(prefix="/api/auth", tags=["Auth"])

class AuthSchema(BaseModel):
    email: EmailStr
    password: str

def hash_pass(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/signup")
def signup(data: AuthSchema, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(email=data.email, hashed_password=hash_pass(data.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": "success", "message": "User registered successfully"}

@router.post("/login")
def login(data: AuthSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or user.hashed_password != hash_pass(data.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return {"status": "success", "message": "Login successful", "user_id": user.id}
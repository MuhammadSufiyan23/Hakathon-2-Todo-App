
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session, select
from typing import Optional
import jwt
import os
from datetime import datetime, timedelta
import bcrypt

from db import get_session
from utils.auth import BETTER_AUTH_SECRET, get_current_user
from models import User as UserModel

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class AuthResponse(BaseModel):
    user: dict
    token: str
    message: str

@router.post("/login", response_model=AuthResponse)
async def login(data: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(
        select(UserModel).where(UserModel.email == data.email)
    ).first()

    if not user or not bcrypt.checkpw(
        data.password.encode(), user.password_hash.encode()
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_data = {
        "sub": str(user.id),
        "userId": str(user.id),
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(days=7),
        "iat": datetime.utcnow()
    }

    token = jwt.encode(token_data, BETTER_AUTH_SECRET, algorithm="HS256")

    return AuthResponse(
        user={"id": user.id, "email": user.email, "name": user.name},
        token=token,
        message="Login successful"
    )

@router.post("/signup", response_model=AuthResponse)
async def signup(data: SignupRequest, session: Session = Depends(get_session)):
    exists = session.exec(
        select(UserModel).where(UserModel.email == data.email)
    ).first()

    if exists:
        raise HTTPException(status_code=400, detail="User already exists")

    password_hash = bcrypt.hashpw(
        data.password.encode(), bcrypt.gensalt()
    ).decode()

    user = UserModel(
        email=data.email,
        password_hash=password_hash,
        name=data.name
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    token_data = {
        "sub": str(user.id),
        "userId": str(user.id),
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(days=7),
        "iat": datetime.utcnow()
    }

    token = jwt.encode(token_data, BETTER_AUTH_SECRET, algorithm="HS256")

    return AuthResponse(
        user={"id": user.id, "email": user.email, "name": user.name},
        token=token,
        message="Signup successful"
    )

@router.post("/logout")
async def logout():
    """
    Logout endpoint (mostly frontend handled with token removal)
    """
    return {"message": "Logout successful"}

@router.get("/profile")
async def profile(current_user=Depends(get_current_user)):
    return current_user

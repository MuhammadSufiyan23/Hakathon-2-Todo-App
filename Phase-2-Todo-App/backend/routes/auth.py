from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
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

# Models for auth requests/responses
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
async def login(login_data: LoginRequest, session: Session = Depends(get_session)):
    """
    Login endpoint that authenticates user and returns JWT token
    """
    if not login_data.email or not login_data.password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    # Look up user in database
    user_query = select(UserModel).where(UserModel.email == login_data.email)
    user = session.exec(user_query).first()

    if not user:
        # To prevent user enumeration, use same error message
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify password hash
    if not bcrypt.checkpw(login_data.password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create JWT token with user information
    token_data = {
        "sub": user.id,  # User ID
        "userId": user.id,  # Better Auth format
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(days=7),  # Token expires in 7 days
        "iat": datetime.utcnow()
    }

    token = jwt.encode(token_data, BETTER_AUTH_SECRET, algorithm="HS256")

    # Return user data and token
    user_data = {
        "id": user.id,
        "email": user.email,
        "name": user.name
    }

    return AuthResponse(
        user=user_data,
        token=token,
        message="Login successful"
    )


@router.post("/signup", response_model=AuthResponse)
async def signup(signup_data: SignupRequest, session: Session = Depends(get_session)):
    """
    Signup endpoint that creates user and returns JWT token
    """
    if not signup_data.email or not signup_data.password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    # Basic email validation
    if "@" not in signup_data.email:
        raise HTTPException(status_code=400, detail="Invalid email format")

    # Check if user already exists
    existing_user_query = select(UserModel).where(UserModel.email == signup_data.email)
    existing_user = session.exec(existing_user_query).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    # Hash the password
    password_hash = bcrypt.hashpw(signup_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Create new user
    new_user = UserModel(
        email=signup_data.email,
        password_hash=password_hash,
        name=signup_data.name
    )

    # Add to session and commit
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Create JWT token with user information
    token_data = {
        "sub": new_user.id,  # User ID
        "userId": new_user.id,  # Better Auth format
        "email": new_user.email,
        "exp": datetime.utcnow() + timedelta(days=7),  # Token expires in 7 days
        "iat": datetime.utcnow()
    }

    token = jwt.encode(token_data, BETTER_AUTH_SECRET, algorithm="HS256")

    # Return user data and token
    user_data = {
        "id": new_user.id,
        "email": new_user.email,
        "name": new_user.name
    }

    return AuthResponse(
        user=user_data,
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
async def get_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current user profile
    """
    # Return user details from the validated JWT token
    return {
        "id": current_user.get("user_id") or current_user.get("userId") or current_user.get("sub") or "unknown",
        "email": current_user.get("email", "unknown@example.com")
    }
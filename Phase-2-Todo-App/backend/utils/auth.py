from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
from dotenv import load_dotenv
import os
from typing import Dict, Optional

# Load environment variables
load_dotenv()

# Get the secret from environment
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

if not BETTER_AUTH_SECRET:
    raise ValueError("BETTER_AUTH_SECRET environment variable is required")

security = HTTPBearer()

class User(BaseModel):
    user_id: str
    email: Optional[str] = None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, str]:
    """
    Dependency to extract and validate JWT token from Authorization header
    Returns user information extracted from the token
    """
    try:
        token = credentials.credentials

        # Decode the JWT token using the secret
        payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])

        # Extract user_id from token (could be in 'sub', 'userId', or 'id' field)
        user_id = payload.get("userId") or payload.get("sub") or payload.get("id")
        email = payload.get("email")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: no user ID found"
            )

        return {"user_id": user_id, "email": email}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except jwt.JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Could not validate credentials: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Authentication error: {str(e)}"
        )
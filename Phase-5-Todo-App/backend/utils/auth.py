from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
from dotenv import load_dotenv
import os
from typing import Dict, Optional

load_dotenv()

BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
if not BETTER_AUTH_SECRET:
    # Use a default secret for development only
    BETTER_AUTH_SECRET = "dev-secret-key-change-in-production-123456"
    print("⚠️  WARNING: Using default auth secret. Set BETTER_AUTH_SECRET environment variable for production!")

security = HTTPBearer()

class User(BaseModel):
    user_id: str
    email: Optional[str] = None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, str]:

    try:
        token = credentials.credentials
        payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])

        user_id = payload.get("userId") or payload.get("sub")
        email = payload.get("email")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        return {"user_id": str(user_id), "email": email}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

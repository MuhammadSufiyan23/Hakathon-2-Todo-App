from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
import os
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the secret from environment
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

if not BETTER_AUTH_SECRET:
    raise ValueError("BETTER_AUTH_SECRET environment variable is required")

security = HTTPBearer()

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

def get_current_user_from_token(token: str) -> Dict[str, str]:
    """
    Extract user information from JWT token
    """
    try:
        # Decode the JWT token using the secret
        payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])

        # Extract user_id from token (could be in 'sub', 'userId', or 'id' field)
        user_id = payload.get("userId") or payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: no user ID found"
            )

        return {"user_id": str(user_id)}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Authentication error"
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, str]:
    """
    Dependency to extract and validate JWT token from Authorization header
    Returns user information extracted from the token
    """
    return get_current_user_from_token(credentials.credentials)

@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    current_user: Dict[str, str] = Depends(get_current_user)
):
    """
    Chat endpoint that accepts a message and returns an AI response.
    Requires valid JWT token in Authorization header.
    """
    try:
        # Extract the message from the request
        user_message = request.message

        # Mock AI response for now
        ai_response = f"I understand your request: {user_message}"

        # Return the response in the required format
        return {
            "reply": ai_response
        }
    except HTTPException:
        # Re-raise HTTP exceptions (like 401)
        raise
    except Exception as e:
        # Log the error for debugging
        print(f"Chat endpoint error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
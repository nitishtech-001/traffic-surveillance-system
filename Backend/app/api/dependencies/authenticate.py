# backend/app/api/dependencies/auth.py
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from app.core.config import settings

security = HTTPBearer()

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    print(data.copy())
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return encoded_jwt

from typing import Dict
from fastapi import Request, HTTPException, status
import jwt  # Assumes you are using PyJWT

def get_current_user(request: Request) -> Dict:
    """Get current user from JWT token"""
    try:
        print("We are at the authentication level...")
        
        # 1. Safely extract the token from cookies
        print(request.cookies)
        token = request.cookies.get("access_token")
        if not token:
            # Changed from 404 to 401 for proper auth semantics
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Authentication cookie token missing"
            )

        print(f"Token found: {token}")
        
        # FIX: Removed 'await' because jwt.decode is synchronous
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        print(f"Decoded payload: {payload}")
        return payload["_id"]

    except jwt.PyJWTError:
        print("User is unauthorized...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

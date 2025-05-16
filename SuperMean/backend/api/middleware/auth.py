"""Authentication Middleware for SuperMean API

This module provides middleware for handling user authentication and authorization
for the SuperMean API endpoints.
"""

import os
import time
from typing import Optional, Dict, List, Callable, Any

from fastapi import Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


# Models
class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data model"""
    username: Optional[str] = None
    scopes: List[str] = []


class User(BaseModel):
    """User model"""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    scopes: List[str] = []


# Helper functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[int] = None) -> str:
    """Create a new JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = time.time() + expires_delta
    else:
        expire = time.time() + ACCESS_TOKEN_EXPIRE_MINUTES * 60
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get the current user from the token"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(username=username, scopes=token_scopes)
    except JWTError:
        raise credentials_exception
    
    # In a real application, you would fetch the user from a database
    # This is a placeholder implementation
    user = User(
        username=token_data.username,
        email=f"{token_data.username}@example.com",
        full_name="Test User",
        disabled=False,
        scopes=token_data.scopes
    )
    
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def requires_scopes(scopes: List[str]):
    """Dependency for requiring specific scopes"""
    async def _requires_scopes(current_user: User = Depends(get_current_user)) -> User:
        for scope in scopes:
            if scope not in current_user.scopes:
                raise HTTPException(
                    status_code=403,
                    detail=f"Not enough permissions. Required scope: {scope}"
                )
        return current_user
    
    return _requires_scopes


# Middleware class for FastAPI
class AuthMiddleware:
    """Authentication middleware for FastAPI"""
    
    async def __call__(self, request: Request, call_next: Callable) -> Any:
        """Process the request through the middleware"""
        # Skip authentication for certain paths
        if request.url.path in ["/api/auth/token", "/api/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Check for Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return HTTPException(
                status_code=401,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract and validate token
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        # Continue processing the request
        return await call_next(request)
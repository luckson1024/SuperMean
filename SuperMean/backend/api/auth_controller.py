#!/usr/bin/env python3
"""
SuperMean API Authentication Controller

This module provides endpoints for user authentication, including login, registration,
and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Any, Optional
from datetime import timedelta

from .auth_middleware import create_access_token, get_current_user, User, JWT_EXPIRATION_MINUTES
from .schemas import ErrorResponse

# Create router
router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)


# Mock user database for demonstration
# In a real application, this would be replaced with a database
USER_DB = {
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "email": "admin@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        "disabled": False,
        "roles": ["admin", "user"]
    },
    "user": {
        "username": "user",
        "full_name": "Regular User",
        "email": "user@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        "disabled": False,
        "roles": ["user"]
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash
    
    In a real application, you would use a proper password hashing library like passlib
    For this example, we're just doing a simple comparison
    
    Args:
        plain_password: The plain text password
        hashed_password: The hashed password
        
    Returns:
        True if the password matches, False otherwise
    """
    # This is a placeholder. In a real app, use proper password verification
    # Example with passlib: return pwd_context.verify(plain_password, hashed_password)
    return hashed_password == "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # "password"


def get_user(username: str) -> Optional[Dict[str, Any]]:
    """
    Get a user from the database
    
    Args:
        username: The username to look up
        
    Returns:
        The user data if found, None otherwise
    """
    if username in USER_DB:
        user_dict = USER_DB[username]
        return user_dict
    return None


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate a user
    
    Args:
        username: The username
        password: The password
        
    Returns:
        The user data if authentication succeeds, None otherwise
    """
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


@router.post("/token", response_model=Dict[str, str])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=JWT_EXPIRATION_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "roles": user["roles"]},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user information
    """
    return current_user


@router.post("/refresh", response_model=Dict[str, str])
async def refresh_token(current_user: User = Depends(get_current_user)):
    """
    Refresh the access token
    """
    access_token_expires = timedelta(minutes=JWT_EXPIRATION_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.username, "roles": current_user.roles},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
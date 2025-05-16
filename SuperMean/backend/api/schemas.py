from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, EmailStr

# Base models for common patterns
class BaseResponse(BaseModel):
    """Base model for API responses"""
    success: bool = True
    message: Optional[str] = None

class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

# Authentication models
class UserBase(BaseModel):
    """Base user information"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """User creation model"""
    password: str

class UserLogin(BaseModel):
    """User login credentials"""
    username: str
    password: str

class User(UserBase):
    """User model with ID"""
    id: str
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime

# Agent models
class AgentBase(BaseModel):
    """Base agent information"""
    name: str
    description: Optional[str] = None
    agent_type: str
    capabilities: List[str] = []
    config: Optional[Dict[str, Any]] = None

class AgentCreate(AgentBase):
    """Agent creation model"""
    pass

class Agent(AgentBase):
    """Agent model with ID"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: str = "idle"

    class Config:
        from_attributes = True

# Mission models
class MissionBase(BaseModel):
    """Base mission information"""
    title: str
    description: str
    goal: str
    priority: int = Field(1, ge=1, le=5)
    parameters: Optional[Dict[str, Any]] = None

class MissionCreate(MissionBase):
    """Mission creation model"""
    agent_ids: List[str] = []

class MissionUpdate(BaseModel):
    """Mission update model"""
    title: Optional[str] = None
    description: Optional[str] = None
    goal: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    parameters: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class Mission(MissionBase):
    """Mission model with ID"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: str = "pending"
    created_by: str
    agents: List[Agent] = []
    results: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

# Skill models
class SkillInfo(BaseModel):
    """Skill information model"""
    name: str
    description: str
    category: str
    version: Optional[str] = None
    last_updated: Optional[datetime] = None
    performance: Optional[Dict[str, Any]] = None

class SkillList(BaseModel):
    """List of skills response"""
    skills: List[SkillInfo]
    total: int

# Memory models
class MemoryEntry(BaseModel):
    """Memory entry model"""
    id: str
    agent_id: Optional[str] = None
    content: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    memory_type: str
    importance: float = 1.0

class MemoryQuery(BaseModel):
    """Memory query parameters"""
    query: str
    agent_id: Optional[str] = None
    memory_type: Optional[str] = None
    limit: int = 10
    min_similarity: float = 0.7

class MemoryQueryResult(BaseModel):
    """Memory query result"""
    entries: List[MemoryEntry]
    total: int
from sqlalchemy import Column, String, Integer, Boolean, Float, DateTime, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from backend.api.database import Base

# Association table for many-to-many relationship between missions and agents
mission_agent = Table(
    "mission_agent",
    Base.metadata,
    Column("mission_id", String, ForeignKey("missions.id")),
    Column("agent_id", String, ForeignKey("agents.id")),
)

# User model
class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # Relationships
    missions = relationship("MissionModel", back_populates="created_by_user")

# Agent model
class AgentModel(Base):
    __tablename__ = "agents"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    agent_type = Column(String)
    capabilities = Column(JSON)
    config = Column(JSON, nullable=True)
    status = Column(String, default="idle")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    agent_metadata = Column(JSON, nullable=True)  # Renamed from metadata to avoid SQLAlchemy reserved name conflict
    
    # Relationships
    missions = relationship("MissionModel", secondary=mission_agent, back_populates="agents")
    memories = relationship("MemoryModel", back_populates="agent")

# Mission model
class MissionModel(Base):
    __tablename__ = "missions"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, index=True)
    description = Column(String)
    goal = Column(String)
    priority = Column(Integer, default=1)
    parameters = Column(JSON, nullable=True)
    status = Column(String, default="pending")
    results = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    created_by = Column(String, ForeignKey("users.id"))
    
    # Relationships
    created_by_user = relationship("UserModel", back_populates="missions")
    agents = relationship("AgentModel", secondary=mission_agent, back_populates="missions")

# Memory model
class MemoryModel(Base):
    __tablename__ = "memories"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, ForeignKey("agents.id"), nullable=True)
    content = Column(JSON)
    memory_metadata = Column(JSON, nullable=True)  # Renamed from metadata
    memory_type = Column(String)
    importance = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agent = relationship("AgentModel", back_populates="memories")
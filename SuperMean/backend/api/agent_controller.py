from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from .database import get_db
from .models import AgentModel
from .auth_middleware import get_current_user
from backend.orchestrator.agent_orchestrator import AgentOrchestrator

# Setup logging
logger = logging.getLogger("agent-controller")

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
    responses={404: {"description": "Not found"}}
)

# Get AgentOrchestrator instance (you'll need to implement this dependency)
async def get_agent_orchestrator():
    # TODO: Implement proper dependency injection
    # This is a placeholder for now
    pass

@router.get("/", response_model=List[Dict[str, Any]])
async def list_agents(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all available agents."""
    try:
        agents = db.query(AgentModel).all()
        return [format_agent_response(agent) for agent in agents]
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{agent_id}", response_model=Dict[str, Any])
async def get_agent(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get details of a specific agent."""
    agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id {agent_id} not found"
        )
    
    return format_agent_response(agent)

@router.post("/", response_model=Dict[str, Any])
async def create_agent(
    agent_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator)
):
    """Create a new agent."""
    try:
        # Create agent in database
        agent = AgentModel(
            name=agent_data["name"],
            description=agent_data.get("description"),
            agent_type=agent_data["agent_type"],
            capabilities=agent_data.get("capabilities", {}),
            config=agent_data.get("config", {}),
            status="initializing"
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)

        # Initialize agent through orchestrator
        try:
            # The agent orchestrator's execute_agent_task method accepts agent_name and task_data
            # We'll use the initialize_task method to set up the agent
            initialization_task = {
                "action": "initialize",
                "agent_type": agent.agent_type,
                "config": agent.config
            }
            
            result = await orchestrator.execute_agent_task(
                agent_name=agent.name,  # Use agent's name as identifier
                task_data=initialization_task
            )
            
            # Update status based on initialization result
            if result.get("status") == "success":
                agent.status = "idle"
            else:
                agent.status = "failed"
            db.commit()
            
        except Exception as e:
            logger.error(f"Error initializing agent: {e}")
            agent.status = "failed"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize agent: {str(e)}"
            )

        return format_agent_response(agent)

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{agent_id}", response_model=Dict[str, Any])
async def update_agent(
    agent_id: str,
    agent_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing agent."""
    agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id {agent_id} not found"
        )

    try:
        # Update allowed fields
        agent.name = agent_data.get("name", agent.name)
        agent.description = agent_data.get("description", agent.description)
        agent.capabilities = agent_data.get("capabilities", agent.capabilities)
        agent.config = agent_data.get("config", agent.config)
        agent.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(agent)

        return format_agent_response(agent)

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator)
):
    """Delete an agent."""
    agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id {agent_id} not found"
        )

    try:
        # First try to terminate the agent through orchestrator
        try:
            termination_task = {
                "action": "terminate",
                "agent_id": agent_id
            }
            await orchestrator.execute_agent_task(
                agent_name=agent.name,
                task_data=termination_task
            )
        except Exception as e:
            logger.warning(f"Error terminating agent {agent_id}: {e}")
            # Continue with deletion even if termination fails

        # Delete from database
        db.delete(agent)
        db.commit()

        return {"message": f"Agent {agent_id} successfully deleted"}

    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{agent_id}/task", response_model=Dict[str, Any])
async def execute_agent_task(
    agent_id: str,
    task_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator)
):
    """Execute a task using a specific agent."""
    # Verify agent exists
    agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id {agent_id} not found"
        )

    try:
        # Execute task through orchestrator
        result = await orchestrator.execute_agent_task(
            agent_name=agent.name,  # Use agent's name as identifier
            task_data=task_data
        )
        
        return {
            "agent_id": agent_id,
            "task_id": result.get("task_id"),
            "status": result.get("status"),
            "result": result.get("output")
        }

    except Exception as e:
        logger.error(f"Error executing task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

def format_agent_response(agent: AgentModel) -> Dict[str, Any]:
    """Format an agent model instance into a response dictionary."""
    return {
        "id": agent.id,
        "name": agent.name,
        "description": agent.description,
        "agent_type": agent.agent_type,
        "capabilities": agent.capabilities,
        "status": agent.status,
        "created_at": agent.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if agent.created_at else None,
        "updated_at": agent.updated_at.strftime("%Y-%m-%dT%H:%M:%SZ") if agent.updated_at else None
    }
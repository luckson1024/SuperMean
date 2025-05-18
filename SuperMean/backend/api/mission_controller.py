from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from .database import get_db
from .models import MissionModel, AgentModel
from .auth_middleware import get_current_user
from backend.orchestrator.mission_control import MissionControl

# Setup logging
logger = logging.getLogger("mission-controller")

router = APIRouter(
    prefix="/missions",
    tags=["missions"],
    responses={404: {"description": "Not found"}}
)

# Get MissionControl instance (you'll need to implement this dependency)
async def get_mission_control():
    # TODO: Implement proper dependency injection
    # This is a placeholder for now
    pass

@router.get("/", response_model=List[Dict[str, Any]])
async def list_missions(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all missions."""
    try:
        missions = db.query(MissionModel).filter(MissionModel.created_by == current_user.id).all()
        return [
            {
                "id": mission.id,
                "title": mission.title,
                "description": mission.description,
                "status": mission.status,
                "priority": mission.priority,
                "created_at": mission.created_at.isoformat() if mission.created_at else None,
                "updated_at": mission.updated_at.isoformat() if mission.updated_at else None,
                "agent_ids": [agent.id for agent in mission.agents]
            }
            for mission in missions
        ]
    except Exception as e:
        logger.error(f"Error listing missions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{mission_id}", response_model=Dict[str, Any])
async def get_mission(
    mission_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get details of a specific mission."""
    mission = db.query(MissionModel).filter(
        MissionModel.id == mission_id,
        MissionModel.created_by == current_user.id
    ).first()
    
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission with id {mission_id} not found"
        )
    
    return {
        "id": mission.id,
        "title": mission.title,
        "description": mission.description,
        "goal": mission.goal,
        "status": mission.status,
        "priority": mission.priority,
        "parameters": mission.parameters,
        "results": mission.results,
        "created_at": mission.created_at.isoformat() if mission.created_at else None,
        "updated_at": mission.updated_at.isoformat() if mission.updated_at else None,
        "agent_ids": [agent.id for agent in mission.agents],
        "created_by": mission.created_by
    }

@router.post("/", response_model=Dict[str, Any])
async def create_mission(
    mission_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    mission_control: MissionControl = Depends(get_mission_control)
):
    """Create a new mission."""
    try:
        # Create mission in database
        mission = MissionModel(
            title=mission_data["title"],
            description=mission_data.get("description"),
            goal=mission_data["goal"],
            priority=mission_data.get("priority", 1),
            parameters=mission_data.get("parameters", {}),
            status="initializing",
            created_by=current_user.id
        )
        db.add(mission)
        db.commit()
        db.refresh(mission)

        # Start mission execution in background
        background_tasks.add_task(
            mission_control.start_mission,
            goal=mission.goal,
            initial_context=mission.parameters,
            mission_id=mission.id
        )

        return {
            "id": mission.id,
            "title": mission.title,
            "description": mission.description,
            "status": mission.status,
            "priority": mission.priority,
            "created_at": mission.created_at.isoformat() if mission.created_at else None
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating mission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{mission_id}", response_model=Dict[str, Any])
async def update_mission(
    mission_id: str,
    mission_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing mission."""
    mission = db.query(MissionModel).filter(
        MissionModel.id == mission_id,
        MissionModel.created_by == current_user.id
    ).first()
    
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission with id {mission_id} not found"
        )

    try:
        # Update allowed fields
        mission.title = mission_data.get("title", mission.title)
        mission.description = mission_data.get("description", mission.description)
        mission.priority = mission_data.get("priority", mission.priority)
        mission.parameters = mission_data.get("parameters", mission.parameters)
        mission.updated_at = datetime.utcnow()
        
        if "status" in mission_data and mission_data["status"] != mission.status:
            # Log status change
            logger.info(f"Mission {mission_id} status changed from {mission.status} to {mission_data['status']}")
            mission.status = mission_data["status"]
        
        db.commit()
        db.refresh(mission)

        return {
            "id": mission.id,
            "title": mission.title,
            "description": mission.description,
            "status": mission.status,
            "priority": mission.priority,
            "parameters": mission.parameters,
            "created_at": mission.created_at.isoformat() if mission.created_at else None,
            "updated_at": mission.updated_at.isoformat() if mission.updated_at else None,
            "agent_ids": [agent.id for agent in mission.agents]
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating mission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{mission_id}")
async def delete_mission(
    mission_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    mission_control: MissionControl = Depends(get_mission_control)
):
    """Delete a mission."""
    mission = db.query(MissionModel).filter(
        MissionModel.id == mission_id,
        MissionModel.created_by == current_user.id
    ).first()
    
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission with id {mission_id} not found"
        )

    try:
        # Try to stop mission if it's running
        try:
            await mission_control.stop_mission(mission_id)
        except Exception as e:
            logger.warning(f"Error stopping mission {mission_id}: {e}")
            # Continue with deletion even if stopping fails

        # Delete from database
        db.delete(mission)
        db.commit()

        return {"message": f"Mission {mission_id} successfully deleted"}

    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting mission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{mission_id}/agents", response_model=Dict[str, Any])
async def assign_agents(
    mission_id: str,
    assignment_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Assign agents to a mission."""
    mission = db.query(MissionModel).filter(
        MissionModel.id == mission_id,
        MissionModel.created_by == current_user.id
    ).first()
    
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission with id {mission_id} not found"
        )

    try:
        # Verify all agents exist
        agent_ids = assignment_data.get("agent_ids", [])
        agents = db.query(AgentModel).filter(AgentModel.id.in_(agent_ids)).all()
        if len(agents) != len(agent_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more agent IDs are invalid"
            )

        # Update mission-agent relationships
        mission.agents = agents
        mission.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(mission)

        return {
            "mission_id": mission.id,
            "agent_ids": [agent.id for agent in mission.agents],
            "updated_at": mission.updated_at.isoformat() if mission.updated_at else None
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error assigning agents to mission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{mission_id}/status", response_model=Dict[str, Any])
async def get_mission_status(
    mission_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    mission_control: MissionControl = Depends(get_mission_control)
):
    """Get the current status and progress of a mission."""
    mission = db.query(MissionModel).filter(
        MissionModel.id == mission_id,
        MissionModel.created_by == current_user.id
    ).first()
    
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission with id {mission_id} not found"
        )

    try:
        # Get detailed status from mission control
        status = await mission_control.get_mission_status(mission_id)
        
        return {
            "mission_id": mission.id,
            "status": mission.status,
            "progress": status.get("progress"),
            "current_phase": status.get("current_phase"),
            "phases_completed": status.get("phases_completed", []),
            "last_update": mission.updated_at.isoformat() if mission.updated_at else None,
            "results": mission.results
        }

    except Exception as e:
        logger.error(f"Error getting mission status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
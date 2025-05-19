from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import uuid
from .database import get_db
from .models import AgentModel
from .auth_middleware import get_current_user
from .schemas import AgentCreate, AgentUpdate, Agent, AgentTask, AgentTaskResponse, AgentStatus
from backend.orchestrator.agent_orchestrator import AgentOrchestrator
from SuperMean.backend.models.model_router import ModelRouter
from SuperMean.backend.memory.agent_memory import AgentMemory
from SuperMean.backend.agents.code_transformer_agent import CodeTransformerAgent
from SuperMean.backend.memory.agent_memory import AgentMemory
from .dependencies import get_agent_orchestrator
logger = logging.getLogger("agent-controller")

router = APIRouter(prefix="/agents", tags=["agents"])

class AgentStateManager:
    """Manages agent state transitions and validation using First Principles."""
    # Rate limiting configuration
    _rate_limits = {
        'REQUESTS_PER_MINUTE': 60,  # Default requests per minute per agent
        'BURST_LIMIT': 10,          # Maximum burst of requests
        'COOLDOWN_PERIOD': 60       # Cooldown period in seconds after hitting limit
    }
    
    # Rate limiting state tracking
    _request_counts = {}  # Format: {agent_id: [(timestamp, count), ...]}
    _cooldown_agents = set()  # Agents currently in cooldown
    
    @classmethod
    def _check_rate_limit(cls, agent_id: str) -> bool:
        """
        Check if an agent has exceeded rate limits.
        Returns True if within limits, False if exceeded.
        """
        current_time = datetime.utcnow()
        
        # Remove old entries and get current minute's requests
        if agent_id in cls._request_counts:
            # Keep only last minute's worth of requests
            cls._request_counts[agent_id] = [
                (ts, count) for ts, count in cls._request_counts[agent_id]
                if (current_time - ts).total_seconds() < 60
            ]
            
            # Calculate total requests in last minute
            total_requests = sum(count for _, count in cls._request_counts[agent_id])
            
            # Check cooldown state
            if agent_id in cls._cooldown_agents:
                last_request = cls._request_counts[agent_id][-1][0] if cls._request_counts[agent_id] else None
                if last_request and (current_time - last_request).total_seconds() >= cls._rate_limits['COOLDOWN_PERIOD']:
                    cls._cooldown_agents.remove(agent_id)
                else:
                    return False
            
            # Check rate limits
            if total_requests >= cls._rate_limits['REQUESTS_PER_MINUTE']:
                cls._cooldown_agents.add(agent_id)
                return False
            
            # Check burst limit
            recent_requests = sum(count for ts, count in cls._request_counts[agent_id]
                               if (current_time - ts).total_seconds() < 1)
            if recent_requests >= cls._rate_limits['BURST_LIMIT']:
                return False
            
            # Update request count
            cls._request_counts[agent_id].append((current_time, 1))
        else:
            # First request for this agent
            cls._request_counts[agent_id] = [(current_time, 1)]
        
        return True

    @staticmethod
    def get_column_value(value: str) -> str:
        """Convert string values to valid column values."""
        try:
            if isinstance(value, str):
                return value.upper()
            return str(value)
        except Exception as e:
            logger.error(f"Error converting value {value}: {e}")
            raise ValueError(f"Invalid value: {value}")

    @staticmethod
    def validate_state_transition(current_state: str, new_state: str) -> bool:
        """Validate if a state transition is allowed."""
        try:
            current_state_str = AgentStateManager.get_column_value(current_state)
            new_state_str = AgentStateManager.get_column_value(new_state)
            
            valid_transitions = {
                AgentStatus.INITIALIZING: [AgentStatus.IDLE, AgentStatus.FAILED],
                AgentStatus.IDLE: [AgentStatus.BUSY, AgentStatus.TERMINATED],
                AgentStatus.BUSY: [AgentStatus.IDLE, AgentStatus.FAILED],
                AgentStatus.FAILED: [AgentStatus.INITIALIZING, AgentStatus.TERMINATED],
                AgentStatus.TERMINATED: []
            }
            
            return AgentStatus(new_state_str) in valid_transitions.get(AgentStatus(current_state_str), [])
        except ValueError:
            return False

    @staticmethod
    async def update_agent_state(
        db: Session,
        agent: AgentModel,
        new_state: AgentStatus,
        state_metadata: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None
    ) -> AgentModel:
        """Update agent state with proper validation and error handling."""
        try:
            # 1. State Validation - First Principles
            current_state = agent.status
            if not AgentStateManager.validate_state_transition(current_state, new_state.value):
                raise ValueError(
                    f"Invalid state transition: {current_state} -> {new_state.value}"
                )

            # 2. Rate Limiting Check
            if not AgentStateManager._check_rate_limit(agent.agent_id):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again later."
                )

            # 3. State Update with History
            state_update = {
                "status": new_state.value,
                "updated_at": datetime.utcnow()
            }
            
            # Merge new metadata with existing
            if state_metadata:
                current_metadata = agent.metadata or {}
                current_metadata.update(state_metadata)
                state_update["metadata"] = current_metadata

            # Add transition reason if provided
            if reason:
                state_update["state_reason"] = reason

            # Update model
            for key, value in state_update.items():
                setattr(agent, key, value)

            # Commit changes
            db.commit()
            db.refresh(agent)
            logger.info(f"Agent {agent.agent_id} state updated: {current_state} -> {new_state.value}")
            return agent

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            error_msg = f"Failed to update agent state: {str(e)}"
            logger.error(error_msg)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )

@router.post("/", response_model=Agent)
async def create_agent(
    agent_data: AgentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator)
):
    """Create a new agent with proper schema validation."""
    try:
        # Create agent in database
        agent = AgentModel(
            name=agent_data.name,
            description=agent_data.description,
            agent_type=agent_data.agent_type,
            capabilities=agent_data.capabilities,
            config=agent_data.config,
            status=agent_data.status.value, # type: ignore
            metadata={
                "created_by": current_user.id,
                "initialization_attempts": 0
            }
        )
        
        db.add(agent)
        db.commit()
        db.refresh(agent)

        # Initialize agent
        try:
            initialization_task = AgentTask(
                action="initialize",
                parameters={
                    "agent_type": agent.agent_type,
                    "config": agent.config
                }
            )

            result = await orchestrator.execute_agent_task(
                agent_name=AgentStateManager.get_column_value(agent.name),
                task_data=initialization_task.dict()
            )

            # Update state based on result
            new_state = AgentStatus.IDLE if result.get("status") == "success" else AgentStatus.FAILED
            await AgentStateManager.update_agent_state(
                db,
                agent,
                new_state,
                metadata={
                    "last_initialization": datetime.utcnow().isoformat(),
                    "initialization_result": result
                }
            )

            return Agent.from_orm(agent)

        except Exception as e:
            logger.error(f"Error initializing agent: {e}")
            await AgentStateManager.update_agent_state(
                db,
                agent,
                AgentStatus.FAILED,
                metadata={"initialization_error": str(e)}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize agent: {str(e)}"
            )

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/code_transformer", response_model=Agent)
async def create_code_transformer_agent(
    agent_data: AgentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator)
):
    """
    Create a new code transformer agent using First Principles and ReAct pattern.
    
    First Principles:
    1. Capability Validation - Verify required capabilities exist
    2. Resource Management - Initialize required resources
    3. State Consistency - Ensure proper initialization state
    4. Error Recovery - Handle failures gracefully
    5. Observability - Track agent creation and initialization
    
    ReAct Steps:
    1. Reasoning - Validate and plan agent creation
    2. Acting - Create and initialize agent
    3. Reflecting - Verify and record outcomes
    """
    try:
        # REASONING PHASE
        # 1. Validate required capabilities
        required_capabilities = ["code_analysis", "code_transformation", "dependency_management"]
        missing_capabilities = [cap for cap in required_capabilities if cap not in agent_data.capabilities]
        if missing_capabilities:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required capabilities: {', '.join(missing_capabilities)}"
            )

        # 2. Resource initialization with error handling
        try:
            model_router = ModelRouter()
            agent_id = str(uuid.uuid4())
            agent_memory = AgentMemory(agent_id=agent_id)
            # Integration with skill execution system
            execute_skill_func = orchestrator.get_skill_executor()

        # ACTING PHASE
        # 1. Prepare initial metadata with observability
        initial_metadata = {
            "agent_id": agent_id,
            "created_by": current_user.id,
            "created_at": datetime.utcnow().isoformat(),
            "initialization_attempts": 0,
            "agent_version": "1.0",
            "creation_context": {
                "source": "api",
                "user_role": current_user.role,
                "original_capabilities": agent_data.capabilities
            }
        }

        # 2. Create agent in database with proper state management
        agent_model = AgentModel(
            name=agent_data.name,
            description=agent_data.description,
            agent_type="code_transformer",
            capabilities=set(agent_data.capabilities + required_capabilities),  # Ensure required capabilities
            config=agent_data.config,
            status=AgentStatus.INITIALIZING.value,  # Start in initializing state
            metadata=initial_metadata
        )
        agent_model.agent_id = agent_id

        try:
            db.add(agent_model)
            db.commit()
            db.refresh(agent_model)
        except Exception as e:
            db.rollback()
            logger.error(f"Database error during agent creation: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create agent in database"
            )

        # Create specialized agent instance with core capabilities
        agent = CodeTransformerAgent(
            name=agent_data.name,
            description=agent_data.description,
            model_router=model_router,
            agent_memory=agent_memory,
            execute_skill_func=execute_skill_func
        )

        # Initialize agent configuration
        agent.agent_id = agent_id
        agent.capabilities = agent_data.capabilities
        agent.config = {
            **agent_data.config,
            "initialization_timestamp": datetime.utcnow().isoformat(),
            "agent_type": "code_transformer",
            "version": "1.0"
        }

        db.add(agent)
        db.commit()
        db.refresh(agent)

        # 3. Initialize agent instance and validate configuration
        try:
            # Initialize with extended configuration
            initialization_task = AgentTask(
                action="initialize",
                parameters={
                    "agent_type": agent_model.agent_type,
                    "config": {
                        **agent_model.config,
                        "required_capabilities": required_capabilities,
                        "initialization_context": {
                            "environment": "production",
                            "timeout": 30,  # seconds
                            "retry_policy": {
                                "max_attempts": 3,
                                "backoff_factor": 1.5
                            }
                        }
                    }
                },
                metadata={
                    "priority": "high",
                    "timeout": 30,
                    "created_by": current_user.id
                }
            )

            # Execute initialization with timeout
            result = await orchestrator.execute_agent_task(
                agent_name=AgentStateManager.get_column_value(agent_model.name),
                task_data=initialization_task.dict()
            )

            # Update state based on result
            new_state = AgentStatus.IDLE if result.get("status") == "success" else AgentStatus.FAILED
            await AgentStateManager.update_agent_state(
                db,
                agent_model,
                new_state,
                metadata={
                    "last_initialization": datetime.utcnow().isoformat(),
                    "initialization_result": result
                }
            )

            return Agent.from_orm(agent)

        except Exception as e:
            logger.error(f"Error initializing agent: {e}")
            await AgentStateManager.update_agent_state(
                db,
                agent_model,
                AgentStatus.FAILED,
                metadata={"initialization_error": str(e)}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize agent: {str(e)}"
            )

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{agent_id}/tasks", response_model=AgentTaskResponse)
async def execute_agent_task(
    agent_id: str,
    task: AgentTask,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator)
):
    """Execute a task on a specific agent with rate limiting and state management."""
    try:
        # Get agent from database
        agent = db.query(AgentModel).filter(AgentModel.agent_id == agent_id).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )

        # Check agent state
        current_state = agent.status
        if AgentStatus(current_state) != AgentStatus.IDLE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Agent is {current_state}, must be IDLE to execute tasks"
            )

        # Rate limiting check is handled by update_agent_state
        task_metadata = {
            "current_task": task.dict(),
            "task_start_time": datetime.utcnow().isoformat(),
            "task_context": {
                "user_id": current_user.id,
                "priority": task.priority,
                "expected_duration": task.expected_duration
            }
        }

        # ACTING PHASE
        # 1. State Transition to BUSY
        await AgentStateManager.update_agent_state(
            db,
            agent,
            AgentStatus.BUSY,
            state_metadata=task_metadata,
            reason=f"Starting task: {task.action}"
        )

        try:
            # 2. Task Execution using ReAct pattern
            logger.info(f"Executing task {task.action} with agent {str(agent.name)}")
            result = await orchestrator.execute_agent_task(
                agent_name=str(agent.name),  # Convert SQLAlchemy column to string
                task_data=task.dict()
            )

            # REFLECTING PHASE
            # 1. Record task outcome
            completion_time = datetime.utcnow()
            completion_metadata = {
                "last_task_completion": completion_time.isoformat(),
                "last_task_result": result,
                "task_metrics": {
                    "execution_duration": (completion_time - datetime.fromisoformat(task_metadata["task_start_time"])).total_seconds(),
                    "success": result.get("status") == "completed",
                    "outcome_summary": result.get("summary", "No summary provided")
                }
            }

            # 2. State Transition to IDLE with reflection data
            await AgentStateManager.update_agent_state(
                db,
                agent,
                AgentStatus.IDLE,
                state_metadata=completion_metadata,
                reason=f"Task completed: {task.action}"
            )

            return AgentTaskResponse(
                task_id=result.get("task_id", ""),
                status=result.get("status", "completed"),
                result=result.get("output", {})
            )

        except Exception as e:
            # Error Recovery and Reflection
            error_time = datetime.utcnow()
            error_metadata = {
                "last_error": str(e),
                "error_context": {
                    "error_time": error_time.isoformat(),
                    "task_duration": (error_time - datetime.fromisoformat(task_metadata["task_start_time"])).total_seconds(),
                    "error_type": type(e).__name__,
                    "task_state": task.dict()
                }
            }

            # Update state to FAILED with detailed error context
            await AgentStateManager.update_agent_state(
                db,
                agent,
                AgentStatus.FAILED,
                state_metadata=error_metadata,
                reason=f"Task failed: {type(e).__name__}"
            )
            raise

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error executing task: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )



from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Dict, Any, Optional
import logging
from pydantic import ValidationError

# Import schemas
from .schemas import BaseResponse, ErrorResponse
from .super_agent_schemas import (
    PlanRequest, PlanResponse, PlanStep,
    EvaluationRequest, EvaluationResponse,
    MetaPlanRequest, MetaPlanResponse,
    ToolCreationRequest, ToolCreationResponse,
    ExecutionRequest, ExecutionResponse,
    MemoryResponse # Import the new schema
)

# Import memory modules
from backend.memory.global_memory import GlobalMemory # Import GlobalMemory

# Import SuperAgent components
from backend.super_agent.planner import Planner, PlanningError
from backend.super_agent.evaluator import Evaluator, EvaluationError
from backend.super_agent.meta_planner import MetaPlanner, MetaPlanningError
from backend.super_agent.tool_creator import ToolCreator, ToolCreationError
from backend.super_agent.builder import Builder, BuilderError

# Import model router for LLM access
from backend.models.model_router import ModelRouter

# Setup logging
logger = logging.getLogger("supermean-api")

# Create router
router = APIRouter(
    prefix="/super-agent",
    tags=["super-agent"],
    responses={404: {"model": ErrorResponse}},
)

# Dependencies
def get_model_router():
    """Dependency to get model router instance"""
    # In a real implementation, this would be properly initialized with config
    return ModelRouter()

def get_planner(model_router: ModelRouter = Depends(get_model_router)):
    """Dependency to get planner instance"""
    return Planner(model_router=model_router)

def get_evaluator(model_router: ModelRouter = Depends(get_model_router)):
    """Dependency to get evaluator instance"""
    return Evaluator(model_router=model_router)

def get_meta_planner(
    planner: Planner = Depends(get_planner),
    evaluator: Evaluator = Depends(get_evaluator),
    model_router: ModelRouter = Depends(get_model_router)
):
    """Dependency to get meta planner instance"""
    # In a real implementation, tool_creator would be properly initialized
    tool_creator = ToolCreator(model_router=model_router)
    return MetaPlanner(
        planner=planner,
        evaluator=evaluator,
        tool_creator=tool_creator,
        model_router=model_router
    )

def get_builder(model_router: ModelRouter = Depends(get_model_router)):
    """Dependency to get builder instance"""
    # In a real implementation, this would be properly initialized
    return Builder(model_router=model_router)

def get_global_memory():
    """Dependency to get GlobalMemory instance"""
    # In a real implementation, this would be properly initialized
    return GlobalMemory()

# Custom exception for SuperAgent operations
class SuperAgentOperationError(Exception):
    """Custom exception for SuperAgent operations."""
    def __init__(self, message: str, status_code: int = 500, details: Optional[dict] = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

def validate_plan_request(request: Dict[str, Any]) -> None:
    """Validate plan request data."""
    required_fields = ["goal", "context"]
    for field in required_fields:
        if field not in request:
            raise ValidationError(f"Missing required field: {field}")

    if not isinstance(request["goal"], str) or not request["goal"].strip():
        raise ValidationError("Goal must be a non-empty string")

# API Endpoints
@router.post("/plan", response_model=PlanResponse)
async def create_plan(
    request: PlanRequest,
    planner: Planner = Depends(get_planner),
    memory: GlobalMemory = Depends(get_global_memory)
):
    """Create a plan using the SuperAgent planner with improved error handling."""
    try:
        # Validate request
        validate_plan_request(request.dict())

        # Check memory for similar plans
        existing_plan = await memory.find_similar_plan(request.goal)
        if existing_plan:
            logger.info(f"Found existing plan for goal: {request.goal}")
            return PlanResponse(
                plan=existing_plan["plan"],
                metadata={"source": "memory", "original_created": existing_plan["created_at"]}
            )

        # Create new plan
        try:
            plan = await planner.create_plan(
                goal=request.goal,
                context=request.context,
                constraints=request.constraints
            )
        except PlanningError as e:
            logger.error(f"Planning error: {e}")
            raise SuperAgentOperationError(
                message="Failed to create plan",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                details={"planning_error": str(e)}
            )

        # Store plan in memory
        await memory.store_plan(request.goal, plan)

        return PlanResponse(plan=plan, metadata={"source": "new"})

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except SuperAgentOperationError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"message": e.message, "details": e.details}
        )
    except Exception as e:
        logger.error(f"Unexpected error in create_plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the plan"
        )

@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_execution(
    request: EvaluationRequest,
    evaluator: Evaluator = Depends(get_evaluator)
):
    """Evaluate the execution of a plan"""
    try:
        evaluation = await evaluator.evaluate_execution(
            goal=request.goal,
            plan=request.plan,
            execution_result=request.execution_result
        )
        
        return EvaluationResponse(
            success=True,
            message="Execution evaluated successfully",
            evaluation=evaluation,
            overall_success=evaluation.get("overall_success", False),
            score=evaluation.get("score", 0.0),
            reasoning=evaluation.get("reasoning", ""),
            suggestions=evaluation.get("suggestions", [])
        )
    except EvaluationError as e:
        logger.error(f"Evaluation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {e}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in evaluate_execution: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during evaluation"
        )

@router.post("/meta-plan", response_model=Dict[str, Any])
async def reflect_and_adapt(
    request: Dict[str, Any],
    meta_planner: MetaPlanner = Depends(get_meta_planner)
):
    """Reflect on execution results and decide next steps"""
    try:
        goal = request.get("goal")
        plan = request.get("plan")
        execution_result = request.get("execution_result")
        evaluation = request.get("evaluation")
        
        if not all([goal, plan, execution_result]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Goal, plan, and execution_result are required"
            )
            
        outcome, additional_data = await meta_planner.reflect_and_adapt(
            goal=goal,
            plan=plan,
            execution_result=execution_result,
            evaluation=evaluation
        )
        
        return {
            "success": True,
            "message": "Meta-planning completed successfully",
            "outcome": outcome,
            "additional_data": additional_data
        }
    except MetaPlanningError as e:
        logger.error(f"Meta-planning error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Meta-planning failed: {e}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in reflect_and_adapt: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during meta-planning"
        )

@router.post("/create-tool", response_model=Dict[str, Any])
async def create_tool(
    request: Dict[str, Any],
    tool_creator: ToolCreator = Depends(lambda: ToolCreator(model_router=get_model_router()))
):
    """Create a new tool based on specifications"""
    try:
        tool_spec = request.get("tool_spec")
        if not tool_spec:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tool specification is required"
            )
            
        tool = await tool_creator.create_tool(tool_spec)
        
        return {
            "success": True,
            "message": "Tool created successfully",
            "tool": tool
        }
    except ToolCreationError as e:
        logger.error(f"Tool creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tool creation failed: {e}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in create_tool: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during tool creation"
        )

@router.post("/execute", response_model=ExecutionResponse)
async def execute_plan(
    request: ExecutionRequest,
    builder: Builder = Depends(get_builder)
):
    """Execute a plan using the Builder component with improved error handling."""
    try:
        # Validate execution request
        if not request.plan:
            raise ValidationError("Plan is required for execution")

        try:
            result = await builder.execute_plan(
                plan=request.plan,
                context=request.context or {}
            )
        except Exception as e:
            logger.error(f"Plan execution error: {e}")
            raise SuperAgentOperationError(
                message="Failed to execute plan",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                details={"execution_error": str(e)}
            )

        return ExecutionResponse(result=result)

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except SuperAgentOperationError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"message": e.message, "details": e.details}
        )
    except Exception as e:
        logger.error(f"Unexpected error in execute_plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during plan execution"
        )
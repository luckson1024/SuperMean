from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

# Memory models
class MemoryEntry(BaseModel):
    """Model for a single memory entry"""
    key: str = Field(..., description="The unique identifier for the memory entry")
    value: Any = Field(..., description="The stored data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata about the entry")

class MemoryResponse(BaseModel):
    """Response model for fetching memory entries"""
    success: bool = True
    message: Optional[str] = None
    memory_entries: List[MemoryEntry] = Field([], description="List of memory entries")

# Base models
class SuperAgentResponse(BaseModel):
    """Base response model for SuperAgent API"""
    success: bool = True
    message: Optional[str] = None

# Planning models
class PlanRequest(BaseModel):
    """Request model for creating a plan"""
    goal: str = Field(..., description="The high-level goal to plan for")
    context: Optional[str] = Field(None, description="Additional context for planning")

class PlanStep(BaseModel):
    """Model for a single step in a plan"""
    step_id: int
    action_description: str
    required_inputs: List[str]
    expected_output: str
    suggested_executor: str
    validation_criteria: Optional[List[str]] = None
    fallback_strategy: Optional[str] = None
    parallel_execution: Optional[bool] = False
    estimated_complexity: Optional[str] = None

class PlanResponse(SuperAgentResponse):
    """Response model for plan creation"""
    plan: List[PlanStep]

# Evaluation models
class EvaluationRequest(BaseModel):
    """Request model for evaluating execution"""
    goal: str
    plan: List[Dict[str, Any]]
    execution_result: Dict[str, Any]

class EvaluationResponse(SuperAgentResponse):
    """Response model for execution evaluation"""
    evaluation: Dict[str, Any] = Field(..., description="Evaluation results")
    overall_success: bool = Field(..., description="Whether the execution was successful overall")
    score: float = Field(..., description="Numerical score of the execution quality")
    reasoning: str = Field(..., description="Reasoning behind the evaluation")
    suggestions: List[str] = Field([], description="Suggestions for improvement")

# Meta-planning models
class MetaPlanRequest(BaseModel):
    """Request model for meta-planning"""
    goal: str
    plan: List[Dict[str, Any]]
    execution_result: Dict[str, Any]
    evaluation: Optional[Dict[str, Any]] = None

class MetaPlanResponse(SuperAgentResponse):
    """Response model for meta-planning"""
    outcome: Literal["REVISE_PLAN", "CREATE_TOOL", "RETRY_STEP", "FINAL_SUCCESS", "FINAL_FAILURE"]
    additional_data: Optional[Dict[str, Any]] = None

# Tool creation models
class ToolSpecification(BaseModel):
    """Model for tool specification"""
    skill_name: str = Field(..., description="Name of the skill in namespace.verb format")
    description: str = Field(..., description="Description of what the tool does")
    args: List[str] = Field(..., description="Arguments the tool accepts")
    returns: str = Field(..., description="Description of what the tool returns")

class ToolCreationRequest(BaseModel):
    """Request model for tool creation"""
    tool_spec: ToolSpecification

class ToolCreationResponse(SuperAgentResponse):
    """Response model for tool creation"""
    tool: Dict[str, Any] = Field(..., description="Created tool information")

# Execution models
class ExecutionRequest(BaseModel):
    """Request model for plan execution"""
    plan: List[Dict[str, Any]]
    async_execution: bool = Field(False, description="Whether to execute the plan asynchronously")

class ExecutionResponse(SuperAgentResponse):
    """Response model for plan execution"""
    status: str = Field(..., description="Status of the execution")
    result: Optional[Dict[str, Any]] = Field(None, description="Execution results if available")
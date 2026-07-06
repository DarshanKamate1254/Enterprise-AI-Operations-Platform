from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class RouteDecision(BaseModel):
    """Structured routing intent classifier."""
    next_step: str = Field(
        ...,
        description="Target node for execution. Must be one of: 'sql', 'rag', 'api', 'general', 'unsafe'"
    )
    justification: str = Field(..., description="Explanation for selecting this execution path.")


class PlanSteps(BaseModel):
    """Structured step-by-step task breakdown."""
    steps: List[str] = Field(..., description="Sequential list of actions/goals required to solve the query.")
    justification: str = Field(..., description="Reasoning behind this execution strategy.")


class SQLGeneration(BaseModel):
    """Structured SQL statement compiler."""
    query: str = Field(..., description="The executable PostgreSQL SQL query string (read-only SELECT).")
    explanation: str = Field(..., description="Detailed explanation of what database fields are being queried.")


class APIParameter(BaseModel):
    """Key-value parameter for API payloads."""
    key: str = Field(..., description="Parameter key or argument name.")
    value: str = Field(..., description="Parameter value.")


class APIGeneration(BaseModel):
    """Structured external request generator."""
    method: str = Field(..., description="HTTP Method (GET, POST, PUT, DELETE).")
    url: str = Field(..., description="Target endpoint destination URL.")
    payload: List[APIParameter] = Field(default_factory=list, description="JSON body arguments or URL query parameters.")
    explanation: str = Field(..., description="Explanation of what API features are invoked.")


class ReflectionVerdict(BaseModel):
    """Structured evaluation feedback loop response."""
    approved: bool = Field(..., description="True if output matches all requirements; False if revisions are needed.")
    feedback: str = Field(..., description="Constructive critiques to guide the planner in case of failure or rejection.")


class SafetyVerdict(BaseModel):
    """Structured output security scanner validation."""
    is_safe: bool = Field(..., description="True if the response contains no PII, compliance violations, or unsafe queries.")
    reason: str = Field(..., description="Detailed explanation of the safety assessment result.")

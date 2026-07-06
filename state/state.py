from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


def merge_completed_steps(left: Optional[List[str]], right: Optional[List[str]]) -> List[str]:
    """Reducer that merges lists, avoiding duplicate step strings."""
    if left is None:
        left = []
    if right is None:
        right = []
    return left + [item for item in right if item not in left]


class AgentState(TypedDict):
    """
    Global state structure for LangGraph workflow orchestration.
    Maintains conversational logs, planning, tool outcomes, and evaluations.
    """
    # Annotated with add_messages reducer to auto-append chat records
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Core user query and routing decisions
    user_query: str
    route: str  # "sql", "rag", "api", "general", "unsafe"
    
    # Planning variables
    plan: List[str]
    completed_steps: Annotated[List[str], merge_completed_steps]
    
    # Execution outputs from specialized agents
    retrieved_context: List[str]
    sql_query: str
    sql_result: str
    api_payload: str
    api_result: str
    
    # Feedback loop tracking
    reflection_feedback: str
    reflection_attempts: int
    
    # Safety validation outcomes
    safety_verdict: str  # "safe" or "unsafe"
    
    # Final structured answer compilation
    final_report: str

import sys
import os
from typing import Dict, Any, List
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from state.state import AgentState
from agents.router import router_node
from agents.planner import planner_node
from agents.retrieval import retrieval_node
from agents.sql import sql_node
from agents.api import api_node
from agents.reflection import reflection_node
from agents.safety import safety_node
from agents.report import report_node


def merge_node(state: AgentState) -> Dict[str, Any]:
    """
    Passthrough merge node acting as a synchronization boundary
    for parallel Retrieval, SQL, and API node executions.
    """
    return {}


# ----------------------------------------------------
# Conditional Routing Functions
# ----------------------------------------------------
def route_after_router(state: AgentState) -> str:
    """
    Routes query based on Router Agent's classification.
    """
    route = state.get("route")
    if route == "unsafe":
        return "safety"
    elif route == "general":
        return "report"
    else:
        return "planner"


def route_after_reflection(state: AgentState) -> str:
    """
    Determines if a retry is required based on Reflection feedback.
    Loops back to the Planner if changes are needed and retry limit (<3) is not exceeded.
    """
    feedback = state.get("reflection_feedback")
    attempts = state.get("reflection_attempts") or 0
    
    if feedback and attempts < 3:
        return "planner"
    return "safety"


# ----------------------------------------------------
# Build the LangGraph Workflow
# ----------------------------------------------------
workflow = StateGraph(AgentState)

# 1. Add all Agent Nodes
workflow.add_node("router", router_node)
workflow.add_node("planner", planner_node)
workflow.add_node("retrieval", retrieval_node)
workflow.add_node("sql", sql_node)
workflow.add_node("api", api_node)
workflow.add_node("merge", merge_node)
workflow.add_node("reflection", reflection_node)
workflow.add_node("safety", safety_node)
workflow.add_node("report", report_node)

# 2. Configure Transitions starting from START
workflow.add_edge(START, "router")

# Router conditional routing
workflow.add_conditional_edges(
    "router",
    route_after_router,
    {
        "safety": "safety",
        "report": "report",
        "planner": "planner"
    }
)

# Planner parallel fan-out
workflow.add_edge("planner", "retrieval")
workflow.add_edge("planner", "sql")
workflow.add_edge("planner", "api")

# Parallel fan-in merge
workflow.add_edge("retrieval", "merge")
workflow.add_edge("sql", "merge")
workflow.add_edge("api", "merge")

# Merge synchronization to Reflection evaluation
workflow.add_edge("merge", "reflection")

# Reflection conditional retry or progression
workflow.add_conditional_edges(
    "reflection",
    route_after_reflection,
    {
        "planner": "planner",
        "safety": "safety"
    }
)

# Safety progression to Report compilation
workflow.add_edge("safety", "report")

# Report endpoint to END
workflow.add_edge("report", END)

# 3. Compile the Graph with in-memory checkpointer
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)

import sys
import os
from typing import Dict, Any, Optional
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import settings
from state.state import AgentState
from schemas.agent_schemas import PlanSteps
from prompts.agent_prompts import PLANNER_SYSTEM_PROMPT


class PlannerAgent:
    """
    Planner Agent maps user requests to specific subtasks, adapting plans based on feedback loops.
    """
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        if llm is None:
            api_key = settings.llm.openai_api_key or "mock_key"
            llm = ChatOpenAI(
                model=settings.llm.default_chat_model,
                temperature=0.0,
                api_key=api_key
            )
        self.structured_llm = llm.with_structured_output(PlanSteps)
        
        # Build prompt template accepting user query, execution history, and reflection remarks
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", PLANNER_SYSTEM_PROMPT),
            ("human", "User Request: {query}\n\nExecution History: {history}\n\nFeedback from Reflection: {feedback}")
        ])

    def create_plan(self, query: str, history: str = "", feedback: str = "") -> PlanSteps:
        chain = self.prompt | self.structured_llm
        return chain.invoke({
            "query": query,
            "history": history or "None",
            "feedback": feedback or "None"
        })


def planner_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node wrapper for the Planner Agent.
    Updates the plan list in the state.
    """
    query = state.get("user_query") or ""
    history = ", ".join(state.get("completed_steps") or [])
    feedback = state.get("reflection_feedback") or ""

    planner = PlannerAgent()
    plan_decision = planner.create_plan(query, history, feedback)
    
    return {
        "plan": plan_decision.steps,
        "messages": [
            ("assistant", f"[Planner Action] Formulated Plan: {plan_decision.steps}. Justification: {plan_decision.justification}")
        ]
    }

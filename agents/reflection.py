import sys
import os
from typing import Dict, Any, Optional
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import settings
from state.state import AgentState
from schemas.agent_schemas import ReflectionVerdict
from prompts.agent_prompts import REFLECTION_SYSTEM_PROMPT


class ReflectionAgent:
    """
    Reflection Agent evaluates context correctness, checks database outputs,
    and provides feedback for plan adjustment.
    """
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        if llm is None:
            api_key = settings.llm.openai_api_key or "mock_key"
            llm = ChatOpenAI(
                model=settings.llm.default_chat_model,
                temperature=0.0,
                api_key=api_key
            )
        self.structured_llm = llm.with_structured_output(ReflectionVerdict)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", REFLECTION_SYSTEM_PROMPT),
            ("human", "User Intent: {query}\n\nExecution Logs:\n- Plan: {plan}\n- Completed Steps: {completed}\n- SQL Query: {sql_q}\n- SQL Result: {sql_r}\n- RAG Chunks: {rag}\n- API Result: {api_r}")
        ])

    def evaluate_output(
        self,
        query: str,
        plan: str,
        completed: str,
        sql_q: str,
        sql_r: str,
        rag: str,
        api_r: str
    ) -> ReflectionVerdict:
        chain = self.prompt | self.structured_llm
        return chain.invoke({
            "query": query,
            "plan": plan,
            "completed": completed,
            "sql_q": sql_q,
            "sql_r": sql_r,
            "rag": rag,
            "api_r": api_r
        })


def reflection_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node wrapper for the Reflection Agent.
    Updates the reflection_feedback and counts execution attempts.
    """
    query = state.get("user_query") or ""
    plan = str(state.get("plan") or [])
    completed = str(state.get("completed_steps") or [])
    sql_q = state.get("sql_query") or "None"
    sql_r = state.get("sql_result") or "None"
    rag = "\n".join(state.get("retrieved_context") or [])
    api_r = state.get("api_result") or "None"

    agent = ReflectionAgent()
    verdict = agent.evaluate_output(query, plan, completed, sql_q, sql_r, rag, api_r)
    
    attempts = state.get("reflection_attempts") or 0
    new_attempts = attempts + 1

    feedback = verdict.feedback if not verdict.approved else ""

    return {
        "reflection_feedback": feedback,
        "reflection_attempts": new_attempts,
        "messages": [
            ("assistant", f"[Reflection Review] Approved: {verdict.approved}. Attempts: {new_attempts}. Feedback: {verdict.feedback}")
        ]
    }

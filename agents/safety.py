import sys
import os
from typing import Dict, Any, Optional
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import settings
from state.state import AgentState
from schemas.agent_schemas import SafetyVerdict
from prompts.agent_prompts import SAFETY_SYSTEM_PROMPT


class SafetyAgent:
    """
    Safety Agent monitors model prompts, SQL results, and API outputs to prevent PII leaks
    and compliance boundaries violations.
    """
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        if llm is None:
            api_key = settings.llm.openai_api_key or "mock_key"
            llm = ChatOpenAI(
                model=settings.llm.default_chat_model,
                temperature=0.0,
                api_key=api_key
            )
        self.structured_llm = llm.with_structured_output(SafetyVerdict)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SAFETY_SYSTEM_PROMPT),
            ("human", "Assess safety of this execution content:\n\nQuery: {query}\n\nIntermediate Data Contexts:\n- SQL Results: {sql_r}\n- RAG Chunks: {rag}\n- API Results: {api_r}")
        ])

    def scan_safety(self, query: str, sql_r: str, rag: str, api_r: str) -> SafetyVerdict:
        chain = self.prompt | self.structured_llm
        return chain.invoke({
            "query": query,
            "sql_r": sql_r,
            "rag": rag,
            "api_r": api_r
        })


def safety_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node wrapper for the Safety Agent.
    Updates the safety_verdict parameter in the state.
    """
    query = state.get("user_query") or ""
    sql_r = state.get("sql_result") or "None"
    rag = "\n".join(state.get("retrieved_context") or [])
    api_r = state.get("api_result") or "None"

    agent = SafetyAgent()
    verdict = agent.scan_safety(query, sql_r, rag, api_r)
    
    verdict_str = "safe" if verdict.is_safe else "unsafe"

    return {
        "safety_verdict": verdict_str,
        "messages": [
            ("assistant", f"[Safety Scan] Verdict: '{verdict_str}'. Justification: {verdict.reason}")
        ]
    }

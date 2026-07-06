import sys
import os
from typing import Dict, Any, Optional
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import settings
from state.state import AgentState
from prompts.agent_prompts import REPORT_SYSTEM_PROMPT


from monitoring.telemetry import track_node_latency, record_llm_metrics


class ReportAgent:
    """
    Report Agent consolidates all execution outputs (SQL results, RAG contexts, API replies)
    into a polished Markdown document.
    """
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        if llm is None:
            api_key = settings.llm.openai_api_key or "mock_key"
            llm = ChatOpenAI(
                model=settings.llm.default_chat_model,
                temperature=0.0,
                api_key=api_key
            )
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", REPORT_SYSTEM_PROMPT),
            ("human", "Compile a final report for query: {query}\n\nData Contexts:\n- SQL Query: {sql_q}\n- SQL Result: {sql_r}\n- RAG Chunks: {rag}\n- API Result: {api_r}")
        ])

    def compile_report(self, query: str, sql_q: str, sql_r: str, rag: str, api_r: str) -> str:
        chain = self.prompt | self.llm
        response = chain.invoke({
            "query": query,
            "sql_q": sql_q,
            "sql_r": sql_r,
            "rag": rag,
            "api_r": api_r
        })
        record_llm_metrics("report", response, settings.llm.default_chat_model)
        return response.content


def report_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node wrapper for the Report Agent.
    Updates the final_report key in the state.
    """
    with track_node_latency("report"):
        query = state.get("user_query") or ""
        sql_q = state.get("sql_query") or "None"
        sql_r = state.get("sql_result") or "None"
        rag = "\n".join(state.get("retrieved_context") or [])
        api_r = state.get("api_result") or "None"

        agent = ReportAgent()
        report = agent.compile_report(query, sql_q, sql_r, rag, api_r)

        return {
            "final_report": report,
            "messages": [
                ("assistant", report)
            ]
        }

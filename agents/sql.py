import sys
import os
from typing import Dict, Any, Optional
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import settings
from state.state import AgentState
from schemas.agent_schemas import SQLGeneration
from tools.sql import SQLTool
from prompts.agent_prompts import SQL_SYSTEM_PROMPT
from postgres.database import db_session


from monitoring.telemetry import track_node_latency, record_llm_metrics


class SQLAgent:
    """
    SQL Agent parses schemas, generates read-only SQL queries, and fetches relational data.
    """
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        if llm is None:
            api_key = settings.llm.openai_api_key or "mock_key"
            llm = ChatOpenAI(
                model=settings.llm.default_chat_model,
                temperature=0.0,
                api_key=api_key
            )
        self.structured_llm = llm.with_structured_output(SQLGeneration)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SQL_SYSTEM_PROMPT),
            ("human", "Generate SQL for user request: {query}")
        ])

    def generate_sql(self, query: str) -> SQLGeneration:
        chain = self.prompt | self.structured_llm
        response = chain.invoke({"query": query})
        record_llm_metrics("sql", response, settings.llm.default_chat_model)
        return response


from agents.security import validate_sql_syntax_and_whitelist


def sql_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node wrapper for the SQL Agent.
    Generates and executes SQL query using SQLTool.
    """
    with track_node_latency("sql"):
        query = state.get("user_query") or ""
        
        agent = SQLAgent()
        sql_data = agent.generate_sql(query)
        generated_query = sql_data.query

        result_str = ""
        # 1. SQL Guardrail Validation
        if not validate_sql_syntax_and_whitelist(generated_query):
            result_str = "SQL Validation Error: Query was blocked. Only read-only SELECT commands on permitted tables are authorized."
        else:
            # Execute query using the SQLTool inside a DB session
            try:
                from monitoring.telemetry import record_tool_metric
                record_tool_metric("sql_tool")
                with db_session() as session:
                    tool = SQLTool(session)
                    cols, rows = tool.execute_query(generated_query)
                    
                    # Format results as a text table for context
                    result_lines = [", ".join(cols)]
                    for r in rows:
                        result_lines.append(", ".join(str(val) for val in r))
                    result_str = "\n".join(result_lines)
            except Exception as e:
                result_str = f"SQL Execution Error: {str(e)}"

        # Track steps completion via state reducer delta
        return {
            "sql_query": generated_query,
            "sql_result": result_str,
            "completed_steps": ["sql"],
            "messages": [
                ("assistant", f"[SQL Action] Generated Query:\n```sql\n{generated_query}\n```\nExecution Results:\n```\n{result_str}\n```")
            ]
        }

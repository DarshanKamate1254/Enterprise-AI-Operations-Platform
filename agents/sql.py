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
        return chain.invoke({"query": query})


def sql_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node wrapper for the SQL Agent.
    Generates and executes SQL query using SQLTool.
    """
    query = state.get("user_query") or ""
    
    agent = SQLAgent()
    sql_data = agent.generate_sql(query)
    generated_query = sql_data.query

    result_str = ""
    # Execute query using the SQLTool inside a DB session
    try:
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

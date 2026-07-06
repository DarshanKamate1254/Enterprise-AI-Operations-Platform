import sys
import os
import json
from typing import Dict, Any, Optional
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import settings
from state.state import AgentState
from schemas.agent_schemas import APIGeneration
from tools.api import APITool
from prompts.agent_prompts import API_SYSTEM_PROMPT


class APIAgent:
    """
    API Agent plans and formats outbound HTTP rest operations.
    """
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        if llm is None:
            api_key = settings.llm.openai_api_key or "mock_key"
            llm = ChatOpenAI(
                model=settings.llm.default_chat_model,
                temperature=0.0,
                api_key=api_key
            )
        self.structured_llm = llm.with_structured_output(APIGeneration)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", API_SYSTEM_PROMPT),
            ("human", "Formulate API call for request: {query}")
        ])

    def generate_api_call(self, query: str) -> APIGeneration:
        chain = self.prompt | self.structured_llm
        return chain.invoke({"query": query})


def api_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node wrapper for the API Agent.
    Generates and invokes an HTTP operation via APITool.
    """
    query = state.get("user_query") or ""
    
    agent = APIAgent()
    api_call = agent.generate_api_call(query)
    
    payload_str = json.dumps({
        "method": api_call.method,
        "url": api_call.url,
        "payload": api_call.payload
    }, indent=2)

    result_str = ""
    try:
        # Instantiate and run APITool
        with APITool() as tool:
            response = tool.call_endpoint(
                method=api_call.method,
                url=api_call.url,
                json_data=api_call.payload if api_call.method in ("POST", "PUT") else None,
                params=api_call.payload if api_call.method == "GET" else None
            )
            result_str = json.dumps(response, indent=2)
    except Exception as e:
        result_str = json.dumps({"error": f"API Invocations failed: {str(e)}"}, indent=2)

    # Track steps completion via state reducer delta
    return {
        "api_payload": payload_str,
        "api_result": result_str,
        "completed_steps": ["api"],
        "messages": [
            ("assistant", f"[API Action] Formulated Call:\n```json\n{payload_str}\n```\nResponse Outcomes:\n```json\n{result_str}\n```")
        ]
    }

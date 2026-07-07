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


from monitoring.telemetry import track_node_latency, record_llm_metrics, record_tool_metric


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
        self.structured_llm = llm.with_structured_output(APIGeneration, strict=False)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", API_SYSTEM_PROMPT),
            ("human", "Formulate API call for request: {query}")
        ])

    def generate_api_call(self, query: str) -> APIGeneration:
        chain = self.prompt | self.structured_llm
        response = chain.invoke({"query": query})
        record_llm_metrics("api", response, settings.llm.default_chat_model)
        return response


def api_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node wrapper for the API Agent.
    Generates and invokes an HTTP operation via APITool.
    """
    with track_node_latency("api"):
        query = state.get("user_query") or ""
        route = state.get("route")
        plan = state.get("plan") or []
        
        # Check if an API step is planned or if the route is explicitly api
        api_keywords = {"api", "endpoint", "webhook", "http", "trigger", "url", "request", "post", "get", "put", "delete", "fetch", "external"}
        has_api_step = any(any(kw in step.lower() for kw in api_keywords) for step in plan)
        
        if route != "api" and not has_api_step:
            return {
                "api_payload": "None required",
                "api_result": "No API operations required by the current execution plan.",
                "completed_steps": ["api"],
                "messages": [
                    ("assistant", "[API Action] Bypassed. No API operations were required by the execution plan.")
                ]
            }
            
        agent = APIAgent()
        api_call = agent.generate_api_call(query)
        
        payload_dict = {param.key: param.value for param in api_call.payload}
        
        payload_str = json.dumps({
            "method": api_call.method,
            "url": api_call.url,
            "payload": payload_dict
        }, indent=2)

        result_str = ""
        import httpx
        mcp_success = False
        
        headers = {}
        if settings.mcp.auth_token:
            headers["Authorization"] = f"Bearer {settings.mcp.auth_token}"
            
        try:
            from monitoring.telemetry import record_tool_metric
            record_tool_metric("mcp_tool")
            
            payload = {
                "tool": "rest_api",
                "arguments": {
                    "method": api_call.method,
                    "url": api_call.url,
                    "payload": payload_dict
                }
            }
            response = httpx.post(settings.mcp.server_url, json=payload, headers=headers, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    result_str = json.dumps(data.get("result", {}), indent=2)
                    mcp_success = True
                else:
                    result_str = json.dumps({"error": f"MCP API Execution Error: {data.get('error')}"}, indent=2)
                    mcp_success = True
        except Exception:
            pass
            
        if not mcp_success:
            try:
                # Instantiate and run APITool
                from monitoring.telemetry import record_tool_metric
                record_tool_metric("api_tool")
                with APITool() as tool:
                    response = tool.call_endpoint(
                        method=api_call.method,
                        url=api_call.url,
                        json_data=payload_dict if api_call.method in ("POST", "PUT") else None,
                        params=payload_dict if api_call.method == "GET" else None
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

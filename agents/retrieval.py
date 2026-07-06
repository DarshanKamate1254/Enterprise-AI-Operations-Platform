import sys
import os
from typing import Dict, Any, Optional, List
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import settings
from state.state import AgentState
from tools.retriever import RetrieverTool
from prompts.agent_prompts import RETRIEVAL_SYSTEM_PROMPT


class RetrievalAgent:
    """
    Retrieval Agent searches the corporate policy manuals for relevant guidelines using RetrieverTool.
    """
    def __init__(self, tool: Optional[RetrieverTool] = None, llm: Optional[ChatOpenAI] = None):
        self.tool = tool or RetrieverTool()
        if llm is None:
            api_key = settings.llm.openai_api_key or "mock_key"
            llm = ChatOpenAI(
                model=settings.llm.default_chat_model,
                temperature=0.0,
                api_key=api_key
            )
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", RETRIEVAL_SYSTEM_PROMPT),
            ("human", "Find information about: {query}")
        ])

    def execute_retrieval(self, query: str, category: Optional[str] = None) -> List[str]:
        import httpx
        mcp_success = False
        results = []
        
        headers = {}
        if settings.mcp.auth_token:
            headers["Authorization"] = f"Bearer {settings.mcp.auth_token}"
            
        try:
            payload = {
                "tool": "retriever",
                "arguments": {
                    "query": query,
                    "category": category
                }
            }
            response = httpx.post(settings.mcp.server_url, json=payload, headers=headers, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    results = data.get("result", [])
                    mcp_success = True
        except Exception:
            pass
            
        if not mcp_success:
            results = self.tool.search_policies(query=query, category=category)
        
        # Format results as string segments
        context_blocks = []
        for r in results:
            source = r.get("metadata", {}).get("file_name", "unknown")
            context_blocks.append(f"[Source: {source}] (Score: {r['score']:.2f})\n{r['text']}")
            
        return context_blocks


from monitoring.telemetry import track_node_latency, record_tool_metric


def retrieval_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node wrapper for the Retrieval Agent.
    Updates the retrieved_context and completed_steps.
    """
    with track_node_latency("retrieval"):
        query = state.get("user_query") or ""
        # Category can be inferred from query or routing category filters
        category = state.get("route")
        if category not in {"hr", "finance", "sales", "it", "customer_support", "inventory"}:
            category = None

        # Load tool and run
        agent = RetrievalAgent()
        record_tool_metric("retriever")
        blocks = agent.execute_retrieval(query, category)
        
        # Track steps completion via state reducer delta
        return {
            "retrieved_context": blocks,
            "completed_steps": ["retrieval"],
            "messages": [
                ("assistant", f"[Retrieval Action] Executed semantic policy search. Retrieved {len(blocks)} matches.")
            ]
        }

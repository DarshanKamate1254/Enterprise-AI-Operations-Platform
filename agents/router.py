import sys
import os
from typing import Dict, Any, Optional
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import settings
from state.state import AgentState
from schemas.agent_schemas import RouteDecision
from prompts.agent_prompts import ROUTER_SYSTEM_PROMPT


class RouterAgent:
    """
    Router Agent classifies incoming queries to route them to the appropriate subgraph node.
    """
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        if llm is None:
            api_key = settings.llm.openai_api_key or "mock_key"
            llm = ChatOpenAI(
                model=settings.llm.default_chat_model,
                temperature=0.0,
                api_key=api_key
            )
        self.structured_llm = llm.with_structured_output(RouteDecision)
        
        # Build prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", ROUTER_SYSTEM_PROMPT),
            ("human", "Incoming Query: {query}")
        ])

    def route_query(self, query: str) -> RouteDecision:
        chain = self.prompt | self.structured_llm
        return chain.invoke({"query": query})


def router_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node wrapper for the Router Agent.
    Updates the route variable in the graph state.
    """
    query = state.get("user_query") or ""
    if not query and state.get("messages"):
        query = state["messages"][-1].content

    router = RouterAgent()
    decision = router.route_query(query)
    
    return {
        "route": decision.next_step,
        "messages": [
            ("assistant", f"[Routing Decision] Routing query to: '{decision.next_step}'. Justification: {decision.justification}")
        ]
    }

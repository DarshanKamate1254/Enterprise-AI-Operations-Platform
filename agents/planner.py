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


from monitoring.telemetry import track_node_latency, record_llm_metrics


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
        self.llm = llm
        self.structured_llm = llm.with_structured_output(PlanSteps)
        
        # Build prompt template accepting user query, execution history, and reflection remarks
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", PLANNER_SYSTEM_PROMPT),
            ("human", "User Request: {query}\n\nExecution History: {history}\n\nFeedback from Reflection: {feedback}\n\nSummary of past conversation: {summary}")
        ])

    def create_plan(self, query: str, history: str = "", feedback: str = "", summary: str = "") -> PlanSteps:
        chain = self.prompt | self.structured_llm
        response = chain.invoke({
            "query": query,
            "history": history or "None",
            "feedback": feedback or "None",
            "summary": summary or "None"
        })
        record_llm_metrics("planner", response, settings.llm.default_chat_model)
        return response


def summarize_history(messages: list, llm: ChatOpenAI) -> str:
    """
    Summarizes older messages to prevent token bloating.
    """
    if len(messages) < 6:
        return ""
    # Exclude the last 2 messages (usually the latest user and assistant replies)
    to_summarize = messages[:-2]
    history_lines = []
    for msg in to_summarize:
        role = getattr(msg, "type", "user")
        content = getattr(msg, "content", "")
        history_lines.append(f"{role}: {content}")
        
    history_text = "\n".join(history_lines)
    prompt = f"Summarize the key outcomes and requests of this conversation history in 1 short sentence:\n\n{history_text}"
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Could not generate summary: {str(e)}"


def planner_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node wrapper for the Planner Agent.
    Updates the plan list and the conversation_summary in the state.
    """
    with track_node_latency("planner"):
        query = state.get("user_query") or ""
        history = ", ".join(state.get("completed_steps") or [])
        feedback = state.get("reflection_feedback") or ""
        messages = state.get("messages") or []

        planner = PlannerAgent()
        
        # Run Conversation Summarization if context reaches 6 messages
        existing_summary = state.get("conversation_summary") or ""
        new_summary = existing_summary
        
        if len(messages) >= 6:
            new_summary = summarize_history(messages, planner.llm)
            
        plan_decision = planner.create_plan(query, history, feedback, new_summary)
        
        return {
            "plan": plan_decision.steps,
            "conversation_summary": new_summary,
            "messages": [
                ("assistant", f"[Planner Action] Formulated Plan: {plan_decision.steps}. Summary Context: {new_summary}")
            ]
        }

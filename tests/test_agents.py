import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Configure sys.path for test imports
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)

from state.state import AgentState
from agents.router import router_node
from agents.planner import planner_node
from agents.retrieval import retrieval_node
from agents.sql import sql_node
from agents.api import api_node
from agents.reflection import reflection_node
from agents.safety import safety_node
from agents.report import report_node
from schemas.agent_schemas import (
    RouteDecision, PlanSteps, SQLGeneration, APIGeneration, ReflectionVerdict, SafetyVerdict
)


class TestAgentNodes(unittest.TestCase):

    def setUp(self):
        # Base state dictionary mock
        self.state = {
            "messages": [],
            "user_query": "Hello world query",
            "route": "",
            "plan": [],
            "completed_steps": [],
            "retrieved_context": [],
            "sql_query": "",
            "sql_result": "",
            "api_payload": "",
            "api_result": "",
            "reflection_feedback": "",
            "reflection_attempts": 0,
            "safety_verdict": "",
            "final_report": ""
        }

    # 1. ROUTER NODE TEST
    @patch('agents.router.ChatOpenAI')
    def test_router_node(self, mock_chat_openai):
        """Verify the Router node updates the route state parameter."""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        mock_llm.with_structured_output.return_value = lambda x: RouteDecision(
            next_step="sql", justification="Querying employees database"
        )
        
        updates = router_node(self.state)
        self.assertEqual(updates["route"], "sql")
        self.assertTrue(len(updates["messages"]) > 0)

    # 2. PLANNER NODE TEST
    @patch('agents.planner.ChatOpenAI')
    def test_planner_node(self, mock_chat_openai):
        """Verify the Planner node compiles task sequences."""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        mock_llm.with_structured_output.return_value = lambda x: PlanSteps(
            steps=["query db", "generate report"], justification="Requires transactional tables"
        )
        
        updates = planner_node(self.state)
        self.assertEqual(updates["plan"], ["query db", "generate report"])

    # 3. RETRIEVAL NODE TEST
    @patch('httpx.post', side_effect=Exception("Connection Refused"))
    @patch('agents.retrieval.RetrieverTool')
    def test_retrieval_node(self, mock_retriever_tool, mock_httpx_post):
        """Verify the Retrieval node updates context lists."""
        mock_tool_inst = MagicMock()
        mock_retriever_tool.return_value = mock_tool_inst
        mock_tool_inst.search_policies.return_value = [
            {"text": "Leave rules standard details", "score": 0.95, "metadata": {"file_name": "Leave_Policy.md"}}
        ]
        
        updates = retrieval_node(self.state)
        self.assertEqual(len(updates["retrieved_context"]), 1)
        self.assertIn("Leave_Policy.md", updates["retrieved_context"][0])

    @patch('httpx.post', side_effect=Exception("Connection Refused"))
    @patch('agents.retrieval.RetrieverTool')
    def test_retrieval_node_restricted_user(self, mock_retriever_tool, mock_httpx_post):
        """Verify that a standard user's search is restricted to their user_department."""
        mock_tool_inst = MagicMock()
        mock_retriever_tool.return_value = mock_tool_inst
        mock_tool_inst.search_policies.return_value = []
        
        # Setup restricted state
        test_state = self.state.copy()
        test_state["user_role"] = "User"
        test_state["user_department"] = "hr"
        test_state["route"] = "sales"  # Query intent might claim sales but department is HR
        
        retrieval_node(test_state)
        
        # Verify search_policies was called with category='hr'
        mock_tool_inst.search_policies.assert_called_once()
        called_kwargs = mock_tool_inst.search_policies.call_args[1]
        self.assertEqual(called_kwargs.get("category"), "hr")

    @patch('httpx.post', side_effect=Exception("Connection Refused"))
    @patch('agents.retrieval.RetrieverTool')
    def test_retrieval_node_admin_unrestricted(self, mock_retriever_tool, mock_httpx_post):
        """Verify that an Admin user's search is not restricted to their user_department."""
        mock_tool_inst = MagicMock()
        mock_retriever_tool.return_value = mock_tool_inst
        mock_tool_inst.search_policies.return_value = []
        
        # Setup unrestricted Admin state
        test_state = self.state.copy()
        test_state["user_role"] = "Admin"
        test_state["user_department"] = "hr"
        test_state["route"] = "sales"
        
        retrieval_node(test_state)
        
        # Verify search_policies was called with category='sales' (from routing logic)
        mock_tool_inst.search_policies.assert_called_once()
        called_kwargs = mock_tool_inst.search_policies.call_args[1]
        self.assertEqual(called_kwargs.get("category"), "sales")

    @patch('httpx.post', side_effect=Exception("Connection Refused"))
    @patch('agents.retrieval.RetrieverTool')
    def test_retrieval_node_manager_unrestricted(self, mock_retriever_tool, mock_httpx_post):
        """Verify that a Manager user's search is not restricted to their user_department."""
        mock_tool_inst = MagicMock()
        mock_retriever_tool.return_value = mock_tool_inst
        mock_tool_inst.search_policies.return_value = []
        
        # Setup unrestricted Manager state
        test_state = self.state.copy()
        test_state["user_role"] = "Manager"
        test_state["user_department"] = "hr"
        test_state["route"] = "sales"
        
        retrieval_node(test_state)
        
        # Verify search_policies was called with category='sales' (from routing logic)
        mock_tool_inst.search_policies.assert_called_once()
        called_kwargs = mock_tool_inst.search_policies.call_args[1]
        self.assertEqual(called_kwargs.get("category"), "sales")

    # 4. SQL NODE TEST
    @patch('agents.sql.db_session')
    @patch('agents.sql.SQLTool')
    @patch('agents.sql.ChatOpenAI')
    def test_sql_node(self, mock_chat_openai, mock_sql_tool_class, mock_db_session):
        """Verify the SQL node compiles queries and executes read operations."""
        # Mock LLM query generation
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        mock_llm.with_structured_output.return_value = lambda x: SQLGeneration(
            query="SELECT * FROM employees LIMIT 1", explanation="Fetch single employee record"
        )
        
        # Mock SQLTool query execution returning columns and rows
        mock_sql_tool = MagicMock()
        mock_sql_tool_class.return_value = mock_sql_tool
        mock_sql_tool.execute_query.return_value = (["employee_id", "full_name"], [(1, "Devendra Rao")])
        
        updates = sql_node(self.state)
        self.assertEqual(updates["sql_query"], "SELECT * FROM employees LIMIT 1")
        self.assertIn("Devendra Rao", updates["sql_result"])

    # 5. API NODE TEST
    @patch('agents.api.APITool')
    @patch('agents.api.ChatOpenAI')
    def test_api_node(self, mock_chat_openai, mock_api_tool_class):
        """Verify the API node constructs and fires API triggers."""
        # Mock LLM API generation
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        mock_llm.with_structured_output.return_value = lambda x: APIGeneration(
            method="GET", url="http://local-gw/health", payload=[], explanation="Check service availability"
        )
        
        # Mock APITool endpoint request execution
        mock_api_tool = MagicMock()
        mock_api_tool_class.return_value = mock_api_tool
        mock_api_tool.call_endpoint.return_value = {"status_code": 200, "data": {"status": "ok"}}
        
        # Use patch to mock the context manager structure of APITool
        mock_api_tool_context = mock_api_tool_class.return_value
        mock_api_tool_context.__enter__.return_value = mock_api_tool
        
        updates = api_node(self.state)
        self.assertIn("http://local-gw/health", updates["api_payload"])
        self.assertIn("status_code", updates["api_result"])

    # 6. REFLECTION NODE TEST
    @patch('agents.reflection.ChatOpenAI')
    def test_reflection_node(self, mock_chat_openai):
        """Verify the Reflection node updates loop states and records critiques."""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        mock_llm.with_structured_output.return_value = lambda x: ReflectionVerdict(
            approved=False, feedback="Query failed due to missing RAG documents"
        )
        
        updates = reflection_node(self.state)
        self.assertEqual(updates["reflection_feedback"], "Query failed due to missing RAG documents")
        self.assertEqual(updates["reflection_attempts"], 1)

    # 7. SAFETY NODE TEST
    @patch('agents.safety.ChatOpenAI')
    def test_safety_node(self, mock_chat_openai):
        """Verify the Safety node flags security violations."""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        mock_llm.with_structured_output.return_value = lambda x: SafetyVerdict(
            is_safe=True, reason="No PII leaked in execution data"
        )
        
        updates = safety_node(self.state)
        self.assertEqual(updates["safety_verdict"], "safe")

    # 8. REPORT NODE TEST
    @patch('agents.report.ChatOpenAI')
    def test_report_node(self, mock_chat_openai):
        """Verify the Report node compiles final answers."""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        mock_response = MagicMock(content="Final Consolidated Operational Report Details")
        mock_llm.invoke.return_value = mock_response
        mock_llm.return_value = mock_response  # Handle direct callable wrapping
        
        updates = report_node(self.state)
        self.assertEqual(updates["final_report"], "Final Consolidated Operational Report Details")


if __name__ == "__main__":
    unittest.main()

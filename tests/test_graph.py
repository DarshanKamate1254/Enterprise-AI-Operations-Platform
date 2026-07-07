import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Configure sys.path for test imports
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "agents"))

from agents.graph import app
from schemas.agent_schemas import RouteDecision, PlanSteps, SQLGeneration, APIGeneration, ReflectionVerdict, SafetyVerdict


class TestLangGraphOrchestration(unittest.TestCase):

    # 1. TEST DIRECT UNSAFE ROUTING
    @patch('agents.router.ChatOpenAI')
    @patch('agents.safety.ChatOpenAI')
    @patch('agents.report.ChatOpenAI')
    def test_unsafe_query_path(self, mock_report_llm, mock_safety_llm, mock_router_llm):
        """Verify that unsafe inputs skip planning/tools and route directly to Safety."""
        # Router mock -> Unsafe
        mock_router = MagicMock()
        mock_router_llm.return_value = mock_router
        mock_router.with_structured_output.return_value = lambda x: RouteDecision(
            next_step="unsafe", justification="Malicious injection attempt"
        )

        # Safety mock -> Unsafe verdict
        mock_safety = MagicMock()
        mock_safety_llm.return_value = mock_safety
        mock_safety.with_structured_output.return_value = lambda x: SafetyVerdict(
            is_safe=False, reason="Blocked SQL injection payload"
        )

        # Report mock -> Warning notice
        mock_report = MagicMock()
        mock_report_llm.return_value = mock_report
        mock_report_resp = MagicMock(content="Safety Alert: Request Blocked.")
        mock_report.invoke.return_value = mock_report_resp
        mock_report.return_value = mock_report_resp

        # Initialize State Graph run with Checkpointer ID
        config = {"configurable": {"thread_id": "test_thread_unsafe"}}
        initial_state = {
            "messages": [],
            "user_query": "DROP TABLE employees;",
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

        result = app.invoke(initial_state, config=config)

        # Asserts
        self.assertEqual(result["route"], "unsafe")
        self.assertEqual(result["safety_verdict"], "unsafe")
        self.assertEqual(result["final_report"], "Safety Alert: Request Blocked.")
        
        # Verify checkpoint state retrieval
        state_history = app.get_state(config)
        self.assertEqual(state_history.values["route"], "unsafe")

    # 2. TEST GENERAL INTENT ROUTING
    @patch('agents.router.ChatOpenAI')
    @patch('agents.report.ChatOpenAI')
    def test_general_query_path(self, mock_report_llm, mock_router_llm):
        """Verify that general chat queries bypass tools/reflection and go to Report."""
        # Router mock -> General
        mock_router = MagicMock()
        mock_router_llm.return_value = mock_router
        mock_router.with_structured_output.return_value = lambda x: RouteDecision(
            next_step="general", justification="Greeting chit-chat"
        )

        # Report mock -> Response
        mock_report = MagicMock()
        mock_report_llm.return_value = mock_report
        mock_report_resp = MagicMock(content="Hello! How can I assist you with operations today?")
        mock_report.invoke.return_value = mock_report_resp
        mock_report.return_value = mock_report_resp

        config = {"configurable": {"thread_id": "test_thread_general"}}
        initial_state = {
            "messages": [],
            "user_query": "Hi there!",
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

        result = app.invoke(initial_state, config=config)

        self.assertEqual(result["route"], "general")
        self.assertEqual(result["final_report"], "Hello! How can I assist you with operations today?")
        self.assertEqual(result["plan"], [])  # Planner was bypassed

    # 3. TEST REFLECTION RETRY LOOP
    @patch('agents.retrieval.RetrievalAgent')
    @patch('agents.sql.db_session')
    @patch('agents.api.APITool')
    @patch('agents.router.ChatOpenAI')
    @patch('agents.planner.ChatOpenAI')
    @patch('agents.sql.ChatOpenAI')
    @patch('agents.api.ChatOpenAI')
    @patch('agents.reflection.ChatOpenAI')
    @patch('agents.safety.ChatOpenAI')
    @patch('agents.report.ChatOpenAI')
    def test_reflection_retry_loop(
        self, mock_report_llm, mock_safety_llm, mock_reflection_llm, mock_api_llm, mock_sql_llm, mock_planner_llm, mock_router_llm, mock_api_tool, mock_db_session, mock_retrieval_agent_class
    ):
        """Verify that failures in Reflection route back to the Planner for revisions."""
        # Mock RetrievalAgent to prevent unmocked semantic embeddings / RAG backend calls
        mock_retrieval_agent = MagicMock()
        mock_retrieval_agent_class.return_value = mock_retrieval_agent
        mock_retrieval_agent.execute_retrieval.return_value = []

        # Router -> sql
        mock_router = MagicMock()
        mock_router_llm.return_value = mock_router
        mock_router.with_structured_output.return_value = lambda x: RouteDecision(
            next_step="sql", justification="SQL query request"
        )

        # Planner -> steps list
        mock_planner = MagicMock()
        mock_planner_llm.return_value = mock_planner
        mock_planner.with_structured_output.return_value = lambda x: PlanSteps(
            steps=["sql"], justification="Run database lookup"
        )
        mock_planner.invoke.return_value = MagicMock(content="Mocked summary of past logs.")

        # SQL Agent -> Query
        mock_sql = MagicMock()
        mock_sql_llm.return_value = mock_sql
        mock_sql.with_structured_output.return_value = lambda x: SQLGeneration(
            query="SELECT COUNT(*) FROM employees", explanation="Count employees"
        )

        # API Agent -> Query
        mock_api = MagicMock()
        mock_api_llm.return_value = mock_api
        mock_api.with_structured_output.return_value = lambda x: APIGeneration(
            method="GET", url="http://local-gw/health", payload=[], explanation="Mock health check"
        )

        # Mock APITool actions
        mock_api_inst = MagicMock()
        mock_api_tool.return_value = mock_api_inst
        mock_api_inst.call_endpoint.return_value = {"status_code": 200, "data": {"status": "ok"}}
        mock_api_inst.__enter__.return_value = mock_api_inst

        # Reflection -> Mock first call rejected, second call approved
        mock_reflection = MagicMock()
        mock_reflection_llm.return_value = mock_reflection
        
        call_count = 0
        def reflection_side_effect(x):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return ReflectionVerdict(approved=False, feedback="Query returned no columns, try checking alias")
            return ReflectionVerdict(approved=True, feedback="Looks great")
            
        mock_reflection.with_structured_output.return_value = reflection_side_effect

        # Safety -> Safe
        mock_safety = MagicMock()
        mock_safety_llm.return_value = mock_safety
        mock_safety.with_structured_output.return_value = lambda x: SafetyVerdict(
            is_safe=True, reason="Valid result"
        )

        # Report -> Response
        mock_report = MagicMock()
        mock_report_llm.return_value = mock_report
        mock_report_resp = MagicMock(content="Polished DB Data Report.")
        mock_report.invoke.return_value = mock_report_resp
        mock_report.return_value = mock_report_resp

        config = {"configurable": {"thread_id": "test_thread_retry"}}
        initial_state = {
            "messages": [],
            "user_query": "How many employees are in HR?",
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

        result = app.invoke(initial_state, config=config)

        # Assert reflection loop executed twice (increasing attempt count to 2)
        self.assertEqual(result["reflection_attempts"], 2)
        self.assertEqual(result["final_report"], "Polished DB Data Report.")


if __name__ == "__main__":
    unittest.main()

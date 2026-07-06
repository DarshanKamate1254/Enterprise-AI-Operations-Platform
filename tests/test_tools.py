import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Configure sys.path for test imports
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)

from tools.sql import SQLTool
from tools.retriever import RetrieverTool
from tools.api import APITool
from tools.calculator import CalculatorTool
from tools.filesystem import FilesystemTool
from tools.memory import MemoryTool


class TestReusableTools(unittest.TestCase):

    # ----------------------------------------------------
    # SQL TOOL TESTS
    # ----------------------------------------------------
    def test_sql_tool_read_only_enforcement(self):
        """Verify the SQL Tool blocks write operations and schemas changes."""
        mock_session = MagicMock()
        tool = SQLTool(mock_session)
        
        # Safe query
        mock_session.execute.return_value = MagicMock(keys=lambda: ["id"], fetchall=lambda: [(1,)])
        cols, rows = tool.execute_query("SELECT id FROM employees")
        self.assertEqual(cols, ["id"])
        
        # Forbidden queries
        forbidden = [
            "DROP TABLE departments",
            "INSERT INTO employees (full_name) VALUES ('Hacker')",
            "DELETE FROM orders WHERE order_id = 5",
            "ALTER TABLE users ADD COLUMN compromised BOOLEAN"
        ]
        
        for q in forbidden:
            with self.assertRaises(PermissionError):
                tool.execute_query(q)

    # ----------------------------------------------------
    # RETRIEVER TOOL TESTS
    # ----------------------------------------------------
    def test_retriever_tool_execution(self):
        """Verify the Retriever Tool processes local semantic searches correctly."""
        mock_local_retriever = MagicMock()
        mock_local_retriever.retrieve.return_value = [{"text": "Found document content", "score": 0.9}]
        
        tool = RetrieverTool(local_retriever=mock_local_retriever)
        results = tool.search_policies("find leave policy", category="hr")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["text"], "Found document content")
        self.assertEqual(results[0]["score"], 0.9)
        mock_local_retriever.retrieve.assert_called_once_with(
            query="find leave policy",
            category="hr",
            top_k=10,
            rerank_top_n=4
        )

    # ----------------------------------------------------
    # API TOOL TESTS
    # ----------------------------------------------------
    @patch('httpx.Client')
    def test_api_tool_requests(self, mock_client_class):
        """Verify that the API Tool executes request verbs and handles response codes."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_response.headers = {"Content-Type": "application/json"}
        mock_client.request.return_value = mock_response
        
        tool = APITool(client=mock_client)
        resp = tool.call_endpoint("POST", "http://mock-url.com/api", json_data={"data": 123})
        
        self.assertEqual(resp["status_code"], 200)
        self.assertEqual(resp["data"]["success"], True)
        
        # Unsupported method
        with self.assertRaises(ValueError):
            tool.call_endpoint("PATCH", "http://mock-url.com/api")

    # ----------------------------------------------------
    # CALCULATOR TOOL TESTS
    # ----------------------------------------------------
    def test_calculator_tool_evaluation(self):
        """Verify mathematical expression evaluations and security protections."""
        tool = CalculatorTool()
        
        # Safe math
        self.assertEqual(tool.calculate("2 + 3 * 4"), 14)
        self.assertEqual(tool.calculate("(10 - 2) / 2"), 4)
        self.assertEqual(tool.calculate("2 ** 3"), 8)
        self.assertEqual(tool.calculate("-5 + 10"), 5)
        
        # Dangerous code injections
        injections = [
            "__import__('os').system('dir')",
            "eval('1+1')",
            "globals()",
            "import os",
            "x = 5"
        ]
        for expr in injections:
            with self.assertRaises(ValueError):
                tool.calculate(expr)

    # ----------------------------------------------------
    # FILESYSTEM TOOL TESTS
    # ----------------------------------------------------
    def test_filesystem_tool_sandboxing(self):
        """Verify filesystem actions can read/write inside sandbox but block path traversals."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tool = FilesystemTool(temp_dir)
            
            # Write and Read inside sandbox
            tool.write_file("nested/test.txt", "File content inside sandbox.")
            content = tool.read_file("nested/test.txt")
            self.assertEqual(content, "File content inside sandbox.")
            
            # Check directory listing
            lst = tool.list_dir("nested")
            self.assertIn("test.txt", lst)
            
            # Traversal attempts
            traversals = [
                "../escape.txt",
                "/etc/passwd",
                "nested/../../outside.log"
            ]
            for path in traversals:
                with self.assertRaises(PermissionError):
                    tool.read_file(path)
                with self.assertRaises(PermissionError):
                    tool.write_file(path, "Write leak")

    # ----------------------------------------------------
    # MEMORY TOOL TESTS
    # ----------------------------------------------------
    def test_memory_tool_in_memory(self):
        """Verify memory set/get/clear operations using the in-memory fallback dict."""
        tool = MemoryTool()
        
        tool.store_fact("agent_state", "PLANNING")
        self.assertEqual(tool.retrieve_fact("agent_state"), "PLANNING")
        
        tool.store_fact("key_to_delete", 123)
        tool.clear_memory()
        self.assertIsNone(tool.retrieve_fact("agent_state"))
        self.assertIsNone(tool.retrieve_fact("key_to_delete"))

if __name__ == "__main__":
    unittest.main()

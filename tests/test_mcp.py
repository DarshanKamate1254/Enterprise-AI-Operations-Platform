import os
import sys
import unittest
from fastapi.testclient import TestClient

# Configure sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "mcp-server"))

from mcp_app import app

from config import settings

class TestMCPServer(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.headers = {}
        if settings.mcp.auth_token:
            self.headers["Authorization"] = f"Bearer {settings.mcp.auth_token}"

    def test_list_tools(self):
        response = self.client.get("/mcp/tools", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        tools = response.json()
        self.assertIsInstance(tools, list)
        self.assertTrue(len(tools) > 0)
        tool_names = [t["name"] for t in tools]
        self.assertIn("calculator", tool_names)
        self.assertIn("sql_query", tool_names)

    def test_execute_calculator(self):
        payload = {
            "tool": "calculator",
            "arguments": {"expression": "10 * (2 + 3)"}
        }
        response = self.client.post("/mcp", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["result"], 50)
        self.assertIsNone(data["error"])

    def test_execute_invalid_tool(self):
        payload = {
            "tool": "nonexistent_tool",
            "arguments": {}
        }
        response = self.client.post("/mcp", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("is not registered", data["error"])

if __name__ == "__main__":
    unittest.main()

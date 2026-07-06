import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Configure sys.path for test imports
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "gateway-api"))
sys.path.insert(0, os.path.join(root_dir, "postgres"))

from fastapi.testclient import TestClient
from main import gateway
from auth import create_access_token


class TestAPIGateway(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(gateway)

    # 1. LOGIN API TESTS
    @patch('main.UserRepository')
    @patch('main.db_session')
    def test_login_success(self, mock_db_session, mock_user_repo_class):
        """Verify that a valid user is issued a bearer access token."""
        # Mock database user lookup
        mock_user = MagicMock()
        mock_user.username = "devendra.rao"
        mock_user.role = "Admin"
        mock_user.user_id = 1
        mock_user.password_hash = "mock_hash"
        
        mock_repo = MagicMock()
        mock_repo.get_by_username.return_value = mock_user
        mock_user_repo_class.return_value = mock_repo
        
        # Test login payload
        response = self.client.post("/login", json={"username": "devendra.rao", "password": "password"})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())
        self.assertEqual(response.json()["role"], "Admin")

    @patch('main.UserRepository')
    @patch('main.db_session')
    def test_login_invalid_user(self, mock_db_session, mock_user_repo_class):
        """Verify login fails for non-existent users."""
        mock_repo = MagicMock()
        mock_repo.get_by_username.return_value = None
        mock_user_repo_class.return_value = mock_repo
        
        response = self.client.post("/login", json={"username": "fakeuser", "password": "password"})
        self.assertEqual(response.status_code, 401)

    # 2. CHAT STREAMING TESTS
    @patch('main.graph_app')
    def test_chat_unauthorized(self, mock_graph_app):
        """Verify chat requests without token return 401."""
        response = self.client.post("/chat", json={"message": "hello"})
        self.assertEqual(response.status_code, 401)

    @patch('main.graph_app')
    def test_chat_success_streaming(self, mock_graph_app):
        """Verify authorized chat returns a text/event-stream chunk sequence."""
        # Mock Graph Stream yielding dictionary nodes updates
        mock_graph_app.stream.return_value = [
            {"router": {"route": "sql"}},
            {"sql": {"sql_result": "Success"}}
        ]
        
        # Generate valid mock JWT token
        token = create_access_token({"sub": "devendra.rao", "role": "Admin", "user_id": 1})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = self.client.post("/chat", json={"message": "Show employees"}, headers=headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "text/event-stream; charset=utf-8")
        
        # Confirm stream chunk events are received
        content = response.text
        self.assertIn("router", content)
        self.assertIn("sql", content)

    # 3. UPLOAD RBAC PROTECTION TESTS
    def test_upload_rbac_rejections(self):
        """Verify regular users (non-admin/non-manager) are rejected from upload file routes."""
        # Generate token with User role
        token = create_access_token({"sub": "john.employee", "role": "User", "user_id": 10})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Post mock file content
        file_payload = {"file": ("test.md", b"Mock file policies contents", "text/plain")}
        data_payload = {"category": "hr"}
        
        response = self.client.post("/upload", files=file_payload, data=data_payload, headers=headers)
        # Expect 403 Forbidden
        self.assertEqual(response.status_code, 403)

    @patch('main.httpx.AsyncClient')
    def test_upload_success_rbac(self, mock_async_client_class):
        """Verify Admins are authorized to upload files and trigger ingestion pipeline."""
        # Mock remote RAG Service HTTP POST call
        mock_client = MagicMock()
        mock_async_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "chunks_count": 5}
        mock_client.post.return_value = mock_response
        
        # Generate token with Admin role
        token = create_access_token({"sub": "devendra.rao", "role": "Admin", "user_id": 1})
        headers = {"Authorization": f"Bearer {token}"}
        
        file_payload = {"file": ("test.md", b"Policies content details", "text/plain")}
        data_payload = {"category": "hr"}
        
        # Mock file system writes
        with patch('main.open', unittest.mock.mock_open()):
            with patch('main.os.makedirs'):
                response = self.client.post("/upload", files=file_payload, data=data_payload, headers=headers)
                
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], True)

    # 4. METRICS TESTS
    def test_metrics_retrieval(self):
        """Verify the metrics route compiles Prometheus client statistics."""
        response = self.client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        self.assertIn("gateway_requests_total", response.text)


if __name__ == "__main__":
    unittest.main()

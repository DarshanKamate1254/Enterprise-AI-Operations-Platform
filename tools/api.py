from typing import Dict, Any, Optional
import httpx


class APITool:
    """
    Generic API Client Tool for invoking external endpoints.
    Allows injecting an httpx.Client for mock testing.
    """
    def __init__(self, client: Optional[httpx.Client] = None):
        self.client = client or httpx.Client()

    def call_endpoint(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes HTTP requests safely and returns JSON output or error payloads.
        """
        method = method.upper()
        if method not in {"GET", "POST", "PUT", "DELETE"}:
            raise ValueError(f"HTTP method {method} is not supported by this tool.")

        try:
            response = self.client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                timeout=10.0
            )
            
            # Try to return JSON, else fallback to raw text
            try:
                data = response.json()
            except ValueError:
                data = {"text": response.text}
                
            return {
                "status_code": response.status_code,
                "data": data,
                "headers": dict(response.headers)
            }
            
        except httpx.RequestError as e:
            return {
                "status_code": 500,
                "error": f"HTTP request failed: {str(e)}"
            }

    def close(self):
        if self.client:
            self.client.close()
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# API Documentation

This document describes the API specifications for the **Enterprise AI Operations Platform**.

---

## 🔐 1. Gateway API (`gateway-api`)

Runs on port `8000`. Handles user sessions and agent orchestration.

### Post Login (`POST /login`)
Authenticates user and returns a bearer JWT access token.
- **Request Payload**:
  ```json
  {
    "username": "devendra.rao",
    "password": "password"
  }
  ```
- **Response Format**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
    "token_type": "bearer",
    "role": "Admin",
    "username": "devendra.rao"
  }
  ```

### Chat streaming (`POST /chat`)
Invokes LangGraph orchestrator and streams intermediate agent outputs to the client.
- **Headers**: `Authorization: Bearer <JWT_TOKEN>`
- **Request Payload**:
  ```json
  {
    "message": "List salaries of employees in IT department",
    "thread_id": "session_thread_1234"
  }
  ```
- **Response Format**: `text/event-stream` yielding JSON chunks:
  ```json
  data: {"router": {"route": "sql"}}
  data: {"sql": {"sql_query": "SELECT salary FROM employees...", "sql_result": "..."}}
  data: {"reflection": {"reflection_feedback": "", "reflection_attempts": 1}}
  data: {"report": {"final_report": "### IT Department Salaries..."}}
  ```

### Document Upload (`POST /upload`)
Saves Markdown manuals and triggers vector database uploads. Restricted to Admin and Manager roles.
- **Headers**: `Authorization: Bearer <JWT_TOKEN>`
- **Content-Type**: `multipart/form-data`
- **Form Arguments**:
  - `file`: Markdown file binary (`.md`)
  - `category`: `hr`, `finance`, `sales`, `it`, `customer_support`, or `inventory`
- **Response Format**:
  ```json
  {
    "success": true,
    "message": "File 'Policy.md' uploaded and indexed successfully.",
    "details": {
      "success": true,
      "chunks_count": 8
    }
  }
  ```

### Get Session History (`GET /history`)
Fetches state parameters saved in Redis/Memory checkpointer for a thread.
- **Headers**: `Authorization: Bearer <JWT_TOKEN>`
- **Query Params**: `thread_id=session_thread_1234`
- **Response Format**:
  ```json
  {
    "thread_id": "session_thread_1234",
    "history": {
      "user_query": "List salaries...",
      "route": "sql",
      "sql_query": "SELECT salary...",
      "final_report": "..."
    }
  }
  ```

---

## 📂 2. RAG Service API (`rag-service`)

Runs on port `8001`. Handles semantic searches.

### Retrieve Chunks (`POST /retrieve`)
Fetches similarity matches from Qdrant and reranks them.
- **Request Payload**:
  ```json
  {
    "query": "What are the rules for sick leave?",
    "category": "hr",
    "top_k": 10,
    "rerank_top_n": 4
  }
  ```
- **Response Format**:
  ```json
  {
    "query": "What are the rules...",
    "results": [
      {
        "text": "# Leave Policy\nSick leaves are allowed up to...",
        "score": 0.892,
        "metadata": {
          "file_name": "Leave_Policy.md",
          "category": "hr"
        }
      }
    ]
  }
  ```

---

## 🛠️ 3. MCP Server API (`mcp-server`)

Runs on port `8080`. Handles secure tool executions.

### List Tools (`GET /mcp/tools`)
Exposes metadata of all registered platform tools.
- **Response Format**:
  ```json
  [
    {
      "name": "calculator",
      "description": "Evaluates standard mathematical expressions securely...",
      "parameters": [
        {
          "name": "expression",
          "type": "string",
          "description": "Expression to calculate",
          "required": true
        }
      ]
    }
  ]
  ```

### Call Tool (`POST /mcp`)
Unified endpoint executing tool calls.
- **Request Payload**:
  ```json
  {
    "tool": "calculator",
    "arguments": {
      "expression": "250 * 12"
    }
  }
  ```
- **Response Format**:
  ```json
  {
    "success": true,
    "result": 3000,
    "error": null
  }
  ```

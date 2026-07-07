import sys
import os
import uvicorn
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

# Resolve parent directory imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, HTTPException, Depends, Header, status
from config import settings
from postgres.database import db_session
from tools.calculator import CalculatorTool
from tools.filesystem import FilesystemTool
from tools.api import APITool
from tools.memory import MemoryTool
from tools.retriever import RetrieverTool
from tools.sql import SQLTool

app = FastAPI(
    title="Darshan_AI_Engineer_Ops MCP Server",
    description="Model Context Protocol Server exposing platform tools (SQL, RAG, API, Filesystem, Calculator, Memory).",
    version="1.0.0"
)

# Initialize static tools
calculator_tool = CalculatorTool()
# Sandbox filesystem to the workspace 'data/' directory
filesystem_tool = FilesystemTool(root_dir="data")
memory_tool = MemoryTool()
retriever_tool = RetrieverTool()

# ----------------------------------------------------
# PYDANTIC API SCHEMAS
# ----------------------------------------------------
class ToolParam(BaseModel):
    name: str
    type: str
    description: str
    required: bool

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: List[ToolParam]

class ToolCallRequest(BaseModel):
    tool: str = Field(..., description="Name of the tool to execute.")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Arguments dictionary matching the tool schema.")

class ToolCallResponse(BaseModel):
    success: bool
    result: Any
    error: Optional[str] = None

# Helper dependency to check optional MCP authentication token
def verify_mcp_auth(authorization: Optional[str] = Header(None)):
    if settings.mcp.auth_token:
        expected = f"Bearer {settings.mcp.auth_token}"
        if not authorization or authorization != expected:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized: Invalid or missing MCP server auth token."
            )

# ----------------------------------------------------
# ENDPOINTS
# ----------------------------------------------------
@app.get("/mcp/tools", response_model=List[ToolDefinition], dependencies=[Depends(verify_mcp_auth)])
def list_tools():
    """
    Exposes metadata of all registered platform tools following MCP schema protocols.
    """
    return [
        ToolDefinition(
            name="calculator",
            description="Evaluates standard mathematical expressions securely via AST compilation.",
            parameters=[
                ToolParam(name="expression", type="string", description="Expression to calculate (e.g. 2 + 2)", required=True)
            ]
        ),
        ToolDefinition(
            name="filesystem",
            description="Runs sandboxed filesystem operations (read_file, write_file, list_dir).",
            parameters=[
                ToolParam(name="operation", type="string", description="One of: 'read', 'write', 'list'", required=True),
                ToolParam(name="path", type="string", description="Relative file path inside the sandbox", required=True),
                ToolParam(name="content", type="string", description="Content to write (required only for write operation)", required=False)
            ]
        ),
        ToolDefinition(
            name="sql_query",
            description="Executes read-only SQL queries against the transactional database.",
            parameters=[
                ToolParam(name="query", type="string", description="The SQL SELECT command to execute", required=True)
            ]
        ),
        ToolDefinition(
            name="retriever",
            description="Searches corporate markdown manuals for relevant text chunks using semantic embeddings.",
            parameters=[
                ToolParam(name="query", type="string", description="The semantic search phrase", required=True),
                ToolParam(name="category", type="string", description="Optional document filter category (hr, sales, etc.)", required=False)
            ]
        ),
        ToolDefinition(
            name="rest_api",
            description="Performs HTTP actions (GET, POST, PUT, DELETE) against API endpoints.",
            parameters=[
                ToolParam(name="method", type="string", description="GET, POST, etc.", required=True),
                ToolParam(name="url", type="string", description="HTTP URL to invoke", required=True),
                ToolParam(name="payload", type="object", description="JSON payload or request parameters", required=False)
            ]
        ),
        ToolDefinition(
            name="memory",
            description="Retrieves, clears, or saves session-level operational data and context facts.",
            parameters=[
                ToolParam(name="operation", type="string", description="'store', 'retrieve', 'clear'", required=True),
                ToolParam(name="key", type="string", description="Fact reference key", required=False),
                ToolParam(name="value", type="string", description="Fact string value (required only for store operation)", required=False)
            ]
        )
    ]

@app.post("/mcp", response_model=ToolCallResponse, dependencies=[Depends(verify_mcp_auth)])
def execute_tool(request: ToolCallRequest):
    """
    Unified entry point executing tool commands securely.
    """
    tool_name = request.tool.lower()
    args = request.arguments
    
    try:
        if tool_name == "calculator":
            expr = args.get("expression")
            if not expr:
                raise ValueError("Missing required argument 'expression'.")
            val = calculator_tool.calculate(expr)
            return ToolCallResponse(success=True, result=val)
            
        elif tool_name == "filesystem":
            op = args.get("operation")
            path = args.get("path")
            if not op or not path:
                raise ValueError("Arguments 'operation' and 'path' are required.")
                
            if op == "read":
                res = filesystem_tool.read_file(path)
            elif op == "write":
                content = args.get("content", "")
                res = filesystem_tool.write_file(path, content)
            elif op == "list":
                res = filesystem_tool.list_dir(path)
            else:
                raise ValueError(f"Unsupported filesystem operation '{op}'.")
            return ToolCallResponse(success=True, result=res)
            
        elif tool_name == "sql_query":
            sql_query = args.get("query")
            if not sql_query:
                raise ValueError("Missing required argument 'query'.")
                
            # Run query inside session context
            with db_session() as session:
                sql_tool = SQLTool(session)
                cols, rows = sql_tool.execute_query(sql_query)
                # Format to JSON list of dicts for clean network transport
                records = []
                for row in rows:
                    records.append(dict(zip(cols, [str(v) for v in row])))
                return ToolCallResponse(success=True, result={"columns": cols, "records": records})
                
        elif tool_name == "retriever":
            query = args.get("query")
            category = args.get("category")
            if not query:
                raise ValueError("Missing required argument 'query'.")
            matches = retriever_tool.search_policies(query=query, category=category)
            return ToolCallResponse(success=True, result=matches)
            
        elif tool_name == "rest_api":
            method = args.get("method")
            url = args.get("url")
            payload = args.get("payload")
            if not method or not url:
                raise ValueError("Arguments 'method' and 'url' are required.")
                
            with APITool() as api_tool:
                res = api_tool.call_endpoint(
                    method=method,
                    url=url,
                    json_data=payload if method in ("POST", "PUT") else None,
                    params=payload if method == "GET" else None
                )
            return ToolCallResponse(success=True, result=res)
            
        elif tool_name == "memory":
            op = args.get("operation")
            key = args.get("key")
            if not op:
                raise ValueError("Missing required argument 'operation'.")
                
            if op == "store":
                val = args.get("value")
                if not key or val is None:
                    raise ValueError("Key and value are required for memory store.")
                memory_tool.store_fact(key, val)
                return ToolCallResponse(success=True, result="Saved successfully.")
            elif op == "retrieve":
                if not key:
                    raise ValueError("Key is required for memory retrieve.")
                val = memory_tool.retrieve_fact(key)
                return ToolCallResponse(success=True, result=val)
            elif op == "clear":
                memory_tool.clear_memory()
                return ToolCallResponse(success=True, result="Memory cleared.")
            else:
                raise ValueError(f"Unsupported memory operation '{op}'.")
                
        else:
            raise ValueError(f"Tool '{request.tool}' is not registered on this MCP server.")
            
    except Exception as e:
        return ToolCallResponse(success=False, result=None, error=str(e))

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "service": "mcp-server"}

if __name__ == "__main__":
    uvicorn.run("mcp_app:app", host="0.0.0.0", port=8080, reload=True)

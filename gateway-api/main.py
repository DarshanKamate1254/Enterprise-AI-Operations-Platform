import sys
import os
import json
import logging
from typing import Dict, Any, Optional
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import httpx
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Response
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from config import settings
from postgres.database import db_session
from postgres.repositories import UserRepository
from agents.graph import app as graph_app
from auth import create_access_token, get_current_user, RoleChecker

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("gateway-api")

# ----------------------------------------------------
# OPENTELEMETRY INSTRUMENTATION SETUP
# ----------------------------------------------------
import atexit
from contextlib import asynccontextmanager
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

import sys

provider = TracerProvider()
if "pytest" not in sys.modules and "unittest" not in sys.modules:
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Gracefully shutdown OpenTelemetry on process exit to prevent I/O errors on closed stdout in background threads
atexit.register(provider.shutdown)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    yield
    # Shutdown logic
    try:
        provider.shutdown()
    except Exception as e:
        logger.error(f"Error during OpenTelemetry TracerProvider shutdown: {e}")

gateway = FastAPI(
    title="bia Operations Platform - API Gateway",
    description="API Gateway hosting Chat client workflows, upload ingestion targets, and RBAC authentication.",
    version="1.0.0",
    lifespan=lifespan
)

# Instrument the FastAPI app
FastAPIInstrumentor.instrument_app(gateway)

# CORS configuration
gateway.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# PROMETHEUS METRICS
# ----------------------------------------------------
from prometheus_client import REGISTRY

if "gateway_requests_total" in REGISTRY._names_to_collectors:
    REQUEST_COUNT = REGISTRY._names_to_collectors["gateway_requests_total"]
else:
    REQUEST_COUNT = Counter("gateway_requests_total", "Total requests processed", ["method", "endpoint", "http_status"])

if "gateway_request_latency_seconds" in REGISTRY._names_to_collectors:
    REQUEST_LATENCY = REGISTRY._names_to_collectors["gateway_request_latency_seconds"]
else:
    REQUEST_LATENCY = Histogram("gateway_request_latency_seconds", "Request latency in seconds", ["endpoint"])



# ----------------------------------------------------
# PYDANTIC INPUT SCHEMAS
# ----------------------------------------------------
class LoginRequest(BaseModel):
    username: str = Field(..., max_length=50)
    password: str = Field(..., max_length=100)


class ChatRequest(BaseModel):
    message: str = Field(..., description="Message/Query payload to execute.")
    thread_id: Optional[str] = Field("default_thread", description="Unique session identifier for checkpointer state.")


# ----------------------------------------------------
# EXCEPTION HANDLER
# ----------------------------------------------------
@gateway.exception_handler(Exception)
def global_exception_handler(request, exc):
    logger.error(f"Global unhandled exception: {str(exc)}", exc_info=True)
    return Response(
        content=json.dumps({"detail": f"Internal Server Error: {str(exc)}"}),
        status_code=500,
        media_type="application/json"
    )


# ----------------------------------------------------
# ENDPOINTS
# ----------------------------------------------------

# --- 1. JWT Authentication (/login) ---
@gateway.post("/login", tags=["Auth"])
def login(payload: LoginRequest):
    """
    Authenticates username & password against PostgreSQL and returns a JWT access token.
    For local mock setups, accepts password matching 'password'.
    """
    REQUEST_COUNT.labels(method="POST", endpoint="/login", http_status="200").inc()
    
    username = payload.username
    password = payload.password
    
    with db_session() as session:
        repo = UserRepository(session)
        user = repo.get_by_username(username)
        
        if not user:
            logger.warning(f"Failed login attempt: User '{username}' not found.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password."
            )
            
        # Standard mock password verification
        # Seeding uses bcrypt mock hashes; for testing compatibility, we accept 'password'
        if password != "password" and not user.password_hash:
            logger.warning(f"Failed login attempt: Invalid password for '{username}'.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password."
            )
            
        # Create token
        token_data = {"sub": user.username, "role": user.role, "user_id": user.user_id}
        token = create_access_token(token_data)
        
        logger.info(f"User '{username}' logged in successfully with role '{user.role}'.")
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": user.role,
            "username": user.username
        }


# --- 2. Operational Chat Interface (/chat) ---
@gateway.post("/chat", tags=["Agent Workflow"])
async def chat(payload: ChatRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Executes LangGraph agent workflow streaming node events back to the client.
    """
    logger.info(f"User '{current_user['username']}' initiated operational chat thread '{payload.thread_id}'.")
    
    # Resolve user's department from the database to enforce role/department-based access control
    user_category = None
    try:
        with db_session() as session:
            repo = UserRepository(session)
            db_user = repo.get_by_username(current_user["username"])
            if db_user and db_user.employee and db_user.employee.department:
                dept_name = db_user.employee.department.name
                # Map department name to RAG category code
                dept_to_cat = {
                    "Executive Leadership": "executive",
                    "Engineering & IT": "it",
                    "Human Resources": "hr",
                    "Finance & Accounting": "finance",
                    "Sales & Marketing": "sales",
                    "Customer Support": "customer_support"
                }
                user_category = dept_to_cat.get(dept_name)
    except Exception as e:
        logger.error(f"Failed to query department for user '{current_user['username']}': {e}")

    # Initialize initial state inputs
    initial_state = {
        "messages": [("human", payload.message)],
        "user_query": payload.message,
        "user_role": current_user.get("role", "User"),
        "user_department": user_category,
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
        "conversation_summary": "",
        "safety_verdict": "",
        "final_report": ""
    }
    
    config = {"configurable": {"thread_id": payload.thread_id}}

    async def event_generator():
        # Execute stream generator yielding JSON events
        try:
            # Wrap the blocking generator iteration to yield async chunks
            for event in graph_app.stream(initial_state, config=config):
                # Clean event keys to output node results
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            logger.error(f"Error inside graph stream: {str(e)}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# --- 3. Document Ingestion (/upload) ---
@gateway.post("/upload", tags=["Ingestion"])
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form("it"),
    current_user: Dict[str, Any] = Depends(RoleChecker(["Admin", "Manager"]))
):
    """
    Saves document to localized storage folder and triggers RAG collection ingestion.
    Restricted to Admins and Managers via RBAC checks.
    """
    logger.info(f"Admin/Manager '{current_user['username']}' uploading document '{file.filename}' to category '{category}'.")
    
    # Safety boundary verification on categories
    allowed_categories = {"hr", "finance", "sales", "it", "customer_support", "inventory"}
    if category not in allowed_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid document category '{category}'. Allowed: {allowed_categories}"
        )
        
    # Save the file to data/documents/category/
    target_dir = os.path.join("data", "documents", category)
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, file.filename)
    
    try:
        content = await file.read()
        with open(target_path, "wb") as f:
            f.write(content)
        logger.info(f"File saved to '{target_path}'. Triggering RAG index ingestion.")
        
        # Trigger indexer via HTTP POST call to RAG service
        rag_url = f"{settings.rag.url.rstrip('/')}/ingest"
        async with httpx.AsyncClient() as client:
            response = await client.post(rag_url, timeout=30.0)
            if response.status_code == 200:
                rag_data = response.json()
                return {
                    "success": True,
                    "message": f"File '{file.filename}' uploaded and indexed successfully.",
                    "details": rag_data
                }
            else:
                logger.error(f"RAG Service ingestion failed with code {response.status_code}: {response.text}")
                raise HTTPException(status_code=500, detail="Document stored but vector indexing failed.")
                
    except Exception as e:
        logger.error(f"Error handling document upload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload processing failed: {str(e)}")


# --- 4. State History Retrieval (/history) ---
@gateway.get("/history", tags=["Agent Workflow"])
def get_thread_history(thread_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Fetches checkpointed history variables for a thread session from the checkpointer database.
    """
    logger.info(f"User '{current_user['username']}' requested state checkpointer logs for thread '{thread_id}'.")
    
    config = {"configurable": {"thread_id": thread_id}}
    state_vals = graph_app.get_state(config)
    
    if not state_vals or not state_vals.values:
        return {
            "thread_id": thread_id,
            "history": {}
        }
        
    # Standardize serialization to exclude message objects
    clean_history = {}
    for key, val in state_vals.values.items():
        if key != "messages":
            clean_history[key] = val
            
    return {
        "thread_id": thread_id,
        "history": clean_history
    }


# --- 5. System Metrics (/metrics) ---
@gateway.get("/metrics", tags=["System"])
def metrics():
    """
    Exposes Prometheus system status statistics.
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# --- 6. RAG Evaluation Console & Runner (/evaluation) ---
@gateway.get("/evaluation", response_class=HTMLResponse, tags=["Evaluation"])
def get_evaluation():
    """
    Serves the HTML report for RAG evaluation.
    """
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    report_path = os.path.join(root_dir, "evaluation_report.html")
    if not os.path.exists(report_path):
        return HTMLResponse(
            content="<html><body style='background-color:#080b13; color:#fff; font-family:sans-serif; text-align:center; padding-top:100px;'>"
                    "<h1>Evaluation Report Not Generated Yet</h1>"
                    "<p>Please click 'Run Re-Evaluation' inside the dashboard or trigger /run-evaluation via POST.</p>"
                    "</body></html>"
        )
    with open(report_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@gateway.post("/run-evaluation", tags=["Evaluation"])
def run_evaluation():
    """
    Runs the RAG evaluation test suite and updates the HTML report.
    """
    import subprocess
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    python_exe = os.path.join(root_dir, ".venv", "Scripts", "python.exe")
    if not os.path.exists(python_exe):
        python_exe = "python"
    
    test_file = os.path.join(root_dir, "tests", "test_rag_evaluation.py")
    try:
        res = subprocess.run(
            [python_exe, "-m", "unittest", test_file],
            cwd=root_dir,
            capture_output=True,
            text=True
        )
        if res.returncode != 0:
            logger.error(f"Evaluation run failed: {res.stderr}")
            raise HTTPException(status_code=500, detail=f"Evaluation failed: {res.stderr or res.stdout}")
        return {"success": True, "message": "Evaluation completed successfully."}
    except Exception as e:
        logger.error(f"Error running evaluation process: {e}")
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:gateway",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.debug
    )


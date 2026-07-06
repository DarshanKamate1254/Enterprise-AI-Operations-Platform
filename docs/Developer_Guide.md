# Developer Setup Guide

This guide provides instructions to run and test **Darshan's Multi-Agent AI Operations Platform** locally.

---

## Prerequisites

- **Python 3.10+**
- **Node.js v18+** & **npm**
- **Docker** & **Docker Compose**
- **OpenAI API Key** (configured in `.env`)

---

## 1. Local Environment Variables (`.env`)

Create a `.env` file in the root directory. Use the following baseline:

```bash
# App Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
JWT_SECRET_KEY=temporary-dev-secret-key-change-in-prod
ACCESS_TOKEN_EXPIRE_MINUTES=60

# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres_secure_pass
POSTGRES_DB=enterprise_ai_ops

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis_secure_pass

# Qdrant Vector Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=qdrant_secure_api_key_here

# LLM Providers Configuration
OPENAI_API_KEY=your_openai_api_key_here
DEFAULT_CHAT_MODEL=gpt-4o-mini
DEFAULT_EMBEDDING_MODEL=text-embedding-3-small

# MCP Configuration
MCP_SERVER_URL=http://localhost:8080/mcp
```

---

## 2. Infrastructure Startup

Launch Postgres, Redis, and Qdrant locally:

```bash
docker compose up postgres redis qdrant -d
```

Verify that the containers are running and healthy:

```bash
docker compose ps
```

---

## 3. Database Initialization & Seeding

Initialize relational tables and seed database records from CSV mock files:

```bash
# Install dependencies
pip install -r requirements.txt

# Run seeding script
python -c "from postgres.service import init_db, seed_db_from_csv; from postgres.database import db_session; init_db(); session=db_session().__enter__(); seed_db_from_csv(session, 'data/database'); session.commit()"
```

---

## 4. Run Backends Locally

Start the three Python backends in separate terminals:

### A. Start the MCP Server
```bash
python mcp-server/mcp_app.py
```
*Exposes tools on port `8080`.*

### B. Start the RAG Service
On macOS/Linux:
```bash
export API_PORT=8001
python rag-service/main.py
```
On Windows PowerShell:
```powershell
$env:API_PORT="8001"
python rag-service/main.py
```
On Windows Command Prompt (cmd):
```cmd
set API_PORT=8001
python rag-service/main.py
```
*Exposes RAG endpoints on port `8001`.*

### C. Start the API Gateway
```bash
python gateway-api/main.py
```
*Exposes gateway client routes on port `8000`.*

---

## 5. Run Frontend Locally

Start the React client dashboard:

```bash
cd frontend
npm install
npm run dev
```
*Exposes Vite dev client on `http://localhost:5173`.*

---

## 6. Running Tests

Execute the unit and integration tests using `pytest`:

```bash
# Run all tests
pytest -v

# Run specific agent nodes tests
pytest tests/test_agents.py -v

# Run MCP server tests
pytest tests/test_mcp.py -v
```


------------------------------
Used tool: manage_task
Used tool: schedule

I am waiting for the tests to finish. Once done, I will update the tasks checklist and write the walkthrough.

Edited task.md
Edited walkthrough.md

I have completed the execution phase to resolve the local connection and port conflict issues.

### Summary of Completed Steps
1. **Decoupled RAG Service Port & Host:** Added a dedicated `RAG_SERVICE_URL` setting inside [settings.py](file:///d:/projects/ai_eng/Enterprise-AI-Operations-Platform/config/settings.py). Updated [main.py](file:///d:/projects/ai_eng/Enterprise-AI-Operations-Platform/gateway-api/main.py) and [retriever.py](file:///d:/projects/ai_eng/Enterprise-AI-Operations-Platform/tools/retriever.py) to route RAG requests correctly.
2. **Updated Deployment Definitions:** Injected the new environment variable in [docker-compose.yml](file:///d:/projects/ai_eng/Enterprise-AI-Operations-Platform/docker-compose.yml) and [gateway-api-deployment.yaml](file:///d:/projects/ai_eng/Enterprise-AI-Operations-Platform/kubernetes/gateway-api-deployment.yaml).
3. **Fixed Documentation Syntax:** Updated [Developer_Guide.md](file:///d:/projects/ai_eng/Enterprise-AI-Operations-Platform/docs/Developer_Guide.md) to provide Windows cmd and PowerShell alternatives to setting the port.
4. **Verified via Tests:** Ran `pytest -v`, resulting in all **43 tests passing successfully**.

A detailed breakdown of all modified files and verification output is available in the [walkthrough.md](file:///C:/Users/Darshan/.gemini/antigravity-ide/brain/65e9295d-cebe-496e-9854-dbdd3815afab/walkthrough.md) artifact. 

### How to Start Your Platform Locally Now:
Since you are on Windows, start your services in separate terminals as follows:

1. **RAG Service (Port 8001):**
   * **PowerShell:**
     ```powershell
     $env:API_PORT="8001"
     python rag-service/main.py
     ```
   * **CMD:**
     ```cmd
     set API_PORT=8001
     python rag-service/main.py
     ```
2. **API Gateway (Port 8000):**
   ```powershell
   python gateway-api/main.py
   ```
3. **MCP Server (Port 8080):**
   ```powershell
   python mcp-server/mcp_app.py
   ```
4. **Frontend Dashboard:**
   ```powershell
   cd frontend
   npm run dev
   ```

You should now be able to successfully access the dashboard and log in with your credentials!
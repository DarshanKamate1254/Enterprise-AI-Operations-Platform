# Developer Setup Guide

This guide provides instructions to run and test **AI_OOPS's Multi-Agent AI Operations Platform** locally.

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

---

## 7. RAG Pipeline Evaluation (Ragas Metrics)

The system includes a dedicated RAG evaluation suite located in `tests/test_rag_evaluation.py` that utilizes **Ragas metrics** (Faithfulness, Answer Relevancy, Context Precision, and Context Recall) to grade the pipeline.

### How to Run the Evaluation

1. **Via CLI (Command Line)**:
   Run the evaluation test using `pytest`:
   ```bash
   pytest tests/test_rag_evaluation.py -v
   ```
   Or via `unittest`:
   ```bash
   python -m unittest tests/test_rag_evaluation.py
   ```

2. **Via API Gateways**:
   Trigger the evaluation dynamically via a `POST` request to the API Gateway:
   ```bash
   curl -X POST http://localhost:8000/run-evaluation
   ```

### Modes of Execution

- **Live Mode**: If a valid `OPENAI_API_KEY` is present in your `.env` file, the script connects to the OpenAI API and Ragas to compute standard LLM-based evaluation metrics.
- **Simulated Mode**: If the key is invalid or has expired, the test script automatically detects the authentication issue, falls back to Simulated Mode using local text-similarity and coverage matching, and marks the report with a warning badge.

### Viewing the Results

The evaluation results are generated in two files in the project root:
- `evaluation_report.html` (visual interactive report)
- `evaluation_report.json` (raw metrics summary)

You can view the dashboard report:
1. **Directly**: Double-click or open `evaluation_report.html` in your browser.
2. **Via Gateway**: Access the dashboard served by the API Gateway at `http://localhost:8000/evaluation`.
3. **Inside React UI**: Log into the React Dashboard (`http://localhost:5173`) and navigate to the **Evaluation Center** tab to view the live dashboard and trigger evaluations on demand.
# Folder Structure

This document details the file directory structure of the **Enterprise AI Operations Platform**.

```
enterprise-ai-platform/
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI/CD pipeline script
├── agents/                    # LangGraph agents nodes definitions
│   ├── api.py                 # API Agent logic
│   ├── graph.py               # Main StateGraph orchestration
│   ├── planner.py             # Task Planner Agent logic
│   ├── reflection.py          # Reflection Agent loop logic
│   ├── report.py              # Report compiler Agent
│   ├── retrieval.py           # Retrieval Agent logic
│   ├── router.py              # Intent Router Agent
│   ├── safety.py              # Safety Scanner Agent
│   └── security.py            # Local security regex scanners (PII, injection)
├── config/                    # Settings configurations loader
│   └── settings.py            # Pydantic BaseSettings class mapping
├── data/                      # Relational datasets & documents manuals
│   ├── database/              # PostgreSQL SQL schema and mock relational CSVs
│   └── documents/             # Corporate policies markdown corpus
├── docker/                    # Microservice-specific container configurations
│   ├── frontend.Dockerfile
│   ├── gateway-api.Dockerfile
│   ├── mcp-server.Dockerfile
│   └── rag-service.Dockerfile
├── docs/                      # Architectural manuals & developer guides
│   ├── Architecture.md
│   ├── Developer_Guide.md
│   ├── Deployment_Guide.md
│   ├── API_Documentation.md
│   ├── Agent_Architecture.md
│   └── Folder_Structure.md
├── frontend/                  # React dashboard client project
│   ├── src/
│   │   ├── App.tsx            # Main state and view components
│   │   ├── index.css          # Glassmorphic dark styling rules
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── gateway-api/               # FastAPI endpoint router
│   ├── auth.py                # JWT & RBAC authentication handlers
│   └── main.py                # Gateway API streaming endpoints
├── kubernetes/                # Kubernetes deploy manifests
│   ├── namespace.yaml
│   ├── secrets.yaml
│   ├── postgres-statefulset.yaml
│   ├── redis-deployment.yaml
│   ├── qdrant-statefulset.yaml
│   ├── mcp-server-deployment.yaml
│   ├── rag-service-deployment.yaml
│   ├── gateway-api-deployment.yaml
│   ├── frontend-deployment.yaml
│   └── ingress.yaml
├── mcp-server/                # Model Context Protocol microservice
│   └── mcp_app.py             # Tool registration server
├── monitoring/                # Prometheus & Grafana configurations
│   ├── grafana/
│   ├── prometheus/            # Prometheus scraping configurations
│   └── telemetry/             # OpenTelemetry tracking logic
├── postgres/                  # SQL Database initialization modules
│   ├── database.py            # SQLAlchemy connection pooling
│   ├── models.py              # SQLAlchemy ORM schemas
│   ├── repositories.py        # Generic BaseRepository CRUD pattern
│   ├── schemas.py             # Pydantic validation schemas
│   └── service.py             # Relational DB seeding utilities
├── prompts/                   # System prompt text configurations
│   └── agent_prompts.py       # Centrally configured prompt templates
├── rag-service/               # RAG document loaders & indexers
│   ├── chunker.py             # Text splitting logic
│   ├── loader.py              # Recursive markdown loader
│   ├── main.py                # Retrieval & Ingestion API
│   ├── retriever.py           # Similarity retrieval & Flashrank reranker
│   └── vector_store.py        # Qdrant client bulk uploading
├── schemas/                   # Pydantic agents model responses
│   └── agent_schemas.py
├── state/                     # LangGraph state variables
│   └── state.py               # TypedDict state models
├── tests/                     # Automated pytest suite
│   ├── test_agents.py
│   ├── test_gateway.py
│   ├── test_graph.py
│   ├── test_guardrails.py
│   ├── test_mcp.py
│   ├── test_postgres.py
│   ├── test_rag.py
│   ├── test_telemetry.py
│   └── test_tools.py
├── docker-compose.yml         # Local container orchestration file
├── requirements.txt           # Python dependency locks
└── README.md                  # Flagship user manual document
```

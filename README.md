# Enterprise AI Operations Platform

Welcome to the **Enterprise AI Operations Platform**. This repository hosts the complete codebase, infrastructure configurations, and orchestration pipelines for a state-of-the-art, secure, and observable AI Agent platform.

---

## 📁 Repository Structure

Below is an overview of the directory structure established for the platform:

```
enterprise-ai-platform/
├── frontend/             # User Interfaces (Admin Dashboard, Chat UI, Analytics)
├── gateway-api/          # API Gateway (Routing, Rate Limiting, Request/Response Transformation)
├── auth-service/         # Authentication & Authorization Service (OAuth2, JWT, RBAC)
├── rag-service/          # Retrieval-Augmented Generation Service (Document ingestion, chunking, embeddings)
├── langgraph/            # Multi-agent workflows, state charts, and execution graphs
├── agents/               # Custom Agent definitions, execution engines, and behaviors
├── prompts/              # Centralized prompt management, versioning, and templates
├── tools/                # Agent tools (API integrations, calculator, web search, database querying)
├── mcp-server/           # Model Context Protocol (MCP) server for tool and resource exposure
├── postgres/             # Relational storage configurations, schemas, and migrations
├── redis/                # Caching layer, session storage, and rate-limiting store
├── qdrant/               # Vector Database configurations for semantic search and RAG
├── monitoring/           # Observability Stack
│   ├── grafana/          # Visualization dashboards
│   ├── prometheus/       # Metrics collector and alerting system
│   └── telemetry/        # OpenTelemetry instrumentation and tracing configuration
├── docker/               # Dockerfiles and docker-compose files for local orchestration
├── kubernetes/           # Kubernetes manifests, Helm charts, and deployment configs
├── tests/                # Integration, end-to-end (E2E), and load testing suites
├── docs/                 # Architecture designs, API reference, and user guides
└── scripts/              # Setup, utility, database seeding, and deployment scripts
```

---

## 🛠️ Components & Technologies

### 1. User Interface (`frontend/`)
- Web-based interface for user interaction with AI agents.
- Admin dashboard to manage agent deployments, monitor costs, and adjust model prompts.

### 2. Core API & Security (`gateway-api/`, `auth-service/`)
- Unified entry point for all client applications.
- Robust security using OAuth2, OpenID Connect (OIDC), Role-Based Access Control (RBAC), and API keys.

### 3. Agentic Workflow Orchestration (`langgraph/`, `agents/`, `prompts/`, `tools/`, `mcp-server/`)
- Complex agent communication and state management leveraging **LangGraph**.
- Centralized **prompt registry** for dynamic prompt loading and version control.
- Extensible **tools framework** utilizing the **Model Context Protocol (MCP)** to expose external capabilities directly to LLMs safely.

### 4. RAG & Vector Database (`rag-service/`, `qdrant/`)
- Document ingestion pipelines supporting PDF, Markdown, HTML, and office documents.
- Semantic search powered by **Qdrant** vector database with hybrid search capabilities (dense and sparse embeddings).

### 5. Persistent Storage & Cache (`postgres/`, `redis/`)
- Relational database (**PostgreSQL**) for structured agent data, logs, conversations, and configurations.
- Cache layer (**Redis**) for lightning-fast session storage and latency reduction.

### 6. Observability (`monitoring/`)
- Real-time telemetry using **OpenTelemetry** for tracing.
- Metrics visualization via **Grafana** and scraping via **Prometheus**.

---

## 🚀 Getting Started

Follow the guides in the [docs/](file:///d:/projects/ai_eng/Enterprise-AI-Operations-Platform/docs/) directory to set up your environment and spin up the services locally using [docker/](file:///d:/projects/ai_eng/Enterprise-AI-Operations-Platform/docker/).

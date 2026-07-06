# Platform Architecture

This document describes the architectural layout of **Darshan's Multi-Agent AI Operations Platform**.

The platform is designed around a decoupled, microservices-first architecture to ensure scalability, fault isolation, and independent deployment of the frontend client, API Gateway, RAG pipeline, and Model Context Protocol (MCP) server.

---

## System Architecture Blueprint

The client request enters the API Gateway, which handles security token checks and delegates stateful execution graphs using LangGraph.

```mermaid
flowchart TD
    Client[Web UI / Client] -->|HTTP/WebSockets| GW[Gateway API]
    GW -->|Authenticate| Auth[Auth Service / Local Token Verification]
    GW -->|Execute Workflow| LG[LangGraph Orchestrator]
    
    subgraph Multi-Agent System
        LG --> Router[1. Router Agent]
        Router -->|Route Request| Planner[2. Planner Agent]
        Planner -->|Fetch Internal Policies| RAG_A[3. Retrieval Agent]
        Planner -->|Query Structured DB| SQL_A[4. SQL Agent]
        Planner -->|Invoke Integrations| API_A[5. API Agent]
        
        RAG_A --> Ref[6. Reflection Agent]
        SQL_A --> Ref
        API_A --> Ref
        
        Ref -->|Correct / Refine| Planner
        Ref -->|Approved| Safety[7. Safety Agent]
        Safety -->|Compliance Cleared| Report[8. Report Agent]
      end

    RAG_A -->|Semantic Queries| Qdrant[(Qdrant Vector DB)]
    SQL_A -->|Read/Write Operations| Postgres[(PostgreSQL DB)]
    API_A -->|Tool Triggers| MCP[MCP Server]
    
    LG -->|State Caching| Redis[(Redis State Store)]
    
    %% Monitoring & Observability
    GW -.->|Traces & Logs| OTEL[OpenTelemetry Collector]
    LG -.->|Traces & Logs| OTEL
    OTEL -.->|Scrape Metrics| Prom[Prometheus]
    Prom -.->|Dashboards| Grafana[Grafana]
```

---

## Component Taxonomy

### 1. Client Frontend (React Dashboard)
A single-page React client served by Nginx. Provides access to:
- A live chat interface showing agent updates.
- Ingestion interfaces for corporate manuals.
- Database schema inspection.
- Observability and latency metrics gauges.

### 2. API Gateway (`gateway-api`)
The main entry point for client HTTP traffic, built with FastAPI. It handles:
- **Authentication (JWT & RBAC)**: Verifies user tokens and restricts route privileges (e.g., locking ingestion routes to Admins/Managers).
- **LangGraph Coordination**: Instantiates the StateGraph and streams intermediate state updates to the client via Server-Sent Events (SSE).
- **Distributed Caching**: Backs LangGraph memory checkpointing with Redis.

### 3. Model Context Protocol (MCP) Server (`mcp-server`)
Standardizes tool integrations. Instead of executing commands directly, agents send tool-calling requests to the MCP server. Exposes tools for:
- Database SELECT execution.
- Vector policy retrievals.
- Ast-based calculations.
- Sandboxed file reads/writes.
- HTTP client requests.

### 4. RAG Service (`rag-service`)
Processes document loading and vector index uploads. Handles:
- **Chunking**: Uses LangChain's `RecursiveCharacterTextSplitter`.
- **Embeddings**: Uses OpenAI's `text-embedding-3-small`.
- **Hybrid Retriever**: Similarity vector retrieval inside Qdrant and local reranking via Flashrank.

### 5. Datastore Layer
- **PostgreSQL**: Stores relational, transactional enterprise tables.
- **Qdrant**: Stores embedded text chunks of corporate policy guides.
- **Redis**: Caches LangGraph checkpointing states for session memory preservation.

# Agent Architecture & Coordination

This document describes the design, responsibilities, prompt strategies, and tools for each of the 8 specialized agents in the **Enterprise AI Operations Platform**.

---

## Agent Grid Overview

| Agent Name | Primary Responsibility | Input State | Output Structured Format | Associated Tools (via MCP) |
| :--- | :--- | :--- | :--- | :--- |
| **Router** | Classify query intent and select target subgraph path. | `user_query` | `RouteDecision` | *None (System Guardrails)* |
| **Planner** | Break down request into a sequential plan of subtasks. | `user_query`, `reflection_feedback` | `PlanSteps` | *None* |
| **Retrieval** | Semantic vector searches in Qdrant policy guides. | `user_query`, `route` | `retrieved_context` | `retriever` tool |
| **SQL** | Generate and execute read-only query fetches. | `user_query` | `sql_query`, `sql_result` | `sql_query` tool |
| **API** | Formulate and dispatch REST actions. | `user_query` | `api_payload`, `api_result` | `rest_api` tool |
| **Reflection** | Validate context and retry execution loops on failures. | `sql_result`, `retrieved_context` | `ReflectionVerdict` | *None* |
| **Safety** | Redact PII (emails, cards, hashes) and check safety. | `sql_result`, `retrieved_context` | `SafetyVerdict` | *None (Security Lib)* |
| **Report** | Consolidate logs into a formatted Markdown report. | `sql_result`, `retrieved_context` | `final_report` | *None* |

---

## Agents Deep Dive

### 1. Router Agent
- **Function**: Validates query boundaries and classifies request routes.
- **Security Check**:
  - Automatically triggers prompt injection scans before invoking LLM classifiers.
  - Validates role access limits (e.g. blocks basic `User` role from querying `users` table or `salary` columns).
- **Outputs**: `next_step` ("sql", "rag", "api", "general", "unsafe") and `justification`.

### 2. Planner Agent
- **Function**: Coordinates the sequential task planner steps.
- **Context Summarization**: Automatically runs a history summarization if thread messages grow to 6+ elements to prevent token limits overflow.
- **Outputs**: `steps` list and `justification`.

### 3. Retrieval Agent
- **Function**: Queries internal markdown manuals for corporate answers.
- **Process**: Matches vector embeddings via the MCP `retriever` tool and performs Flashrank reranking.
- **Outputs**: Formatted sources snippets appended to the state `retrieved_context`.

### 4. SQL Agent
- **Function**: Formulates read-only database query definitions.
- **Security Check**: Verifies that generated queries strictly contain `SELECT` commands targeting permitted database tables.
- **Outputs**: Generates `query` string and stores query result in state `sql_result`.

### 5. API Agent
- **Function**: Invokes system endpoint statuses.
- **Process**: Dispatches GET/POST/etc. HTTP queries using the MCP `rest_api` tool.
- **Outputs**: Formatted json string in state `api_result`.

### 6. Reflection Agent
- **Function**: Reviews intermediate task execution metrics.
- **Retry Trigger**: If database queries returned errors, missing columns, or retriever returned empty blocks, reflection sets `approved` = False. This triggers the state machine loop back to the Planner node (up to 3 times).

### 7. Safety Agent
- **Function**: Runs pre-response security validation.
- **PII Redaction**: Searches text strings for credit cards, email addresses, and bcrypt hashes, replacing matches with `[REDACTED_CREDIT_CARD]`, `[REDACTED_EMAIL]`, or `[REDACTED_PASSWORD_HASH]`.

### 8. Report Agent
- **Function**: Renders final compiled markdown data tables or bulleted manuals answers.
- **Outputs**: Formatted markdown string returned as state `final_report` and appended to message thread history.

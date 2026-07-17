import os
from fpdf import FPDF

class BIAProjectPDF(FPDF):
    def header(self):
        # Header on all pages except cover page (page 1)
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(110, 110, 110)
            self.cell(0, 8, 'BIA Multi-Agent Operations Platform - Technical Architecture Overview', 0, 1, 'R')
            self.set_draw_color(220, 220, 220)
            self.line(10, 18, 200, 18)
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(130, 130, 130)
        # Center page number
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_pdf(output_path):
    pdf = BIAProjectPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # ----------------------------------------------------
    # COVER PAGE
    # ----------------------------------------------------
    # Ambient layout spacing
    pdf.ln(30)
    
    # Decorative primary colored bar
    pdf.set_fill_color(59, 130, 246) # Accent Blue
    pdf.rect(10, 48, 190, 6, 'F')
    
    pdf.ln(15)
    pdf.set_font('Helvetica', 'B', 28)
    pdf.set_text_color(24, 30, 45)
    pdf.cell(0, 12, 'BIA PLATFORM', 0, 1, 'L')
    
    pdf.set_font('Helvetica', '', 18)
    pdf.set_text_color(100, 110, 130)
    pdf.cell(0, 10, 'Multi-Agent AI Operations & Governance Manual', 0, 1, 'L')
    
    pdf.ln(15)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 6, 'ARCHITECTURE & CAPABILITIES SPECIFICATION', 0, 1, 'L')
    
    pdf.ln(60)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 5, 'Designed and Built for:', 0, 1, 'L')
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, 'Enterprise Systems Governance and Verification Testing', 0, 1, 'L')
    
    pdf.ln(10)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 5, 'Technology Stack Summary:', 0, 1, 'L')
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, 'LangGraph, FastAPI, PostgreSQL, Redis, Qdrant DB, OpenTelemetry, Prometheus', 0, 1, 'L')
    
    pdf.ln(10)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 5, 'Date of Compilation:', 0, 1, 'L')
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, 'July 2026', 0, 1, 'L')
    
    # ----------------------------------------------------
    # MAIN PAGES
    # ----------------------------------------------------
    pdf.add_page()
    
    # Title: Introduction & System Purpose
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(24, 30, 45)
    pdf.cell(0, 10, '1. Executive System Introduction', 0, 1, 'L')
    pdf.ln(4)
    
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(60, 60, 60)
    intro_txt = (
        "The BIA Platform is a production-grade, stateful, and observable multi-agent AI system designed "
        "for corporate database interactions, compliance monitoring, and policy inquiries. By orchestrating "
        "specialized LLM agents through a cyclic state graph, the platform automates natural language processing, "
        "relational SQL queries, unstructured documentation search (RAG), and data sanitization."
    )
    pdf.multi_cell(0, 6, intro_txt)
    pdf.ln(6)
    
    # Section: Core Operations
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, '2. Core Platform Capabilities & Operations', 0, 1, 'L')
    pdf.ln(4)
    
    operations = [
      ("Structured SQL Queries", 
       "Allows users to extract information from relational tables using plain English prompts. The system inspects schema constraints, maps references, joins tables, and runs a read-only SELECT statement."),
      ("Unstructured Policy Search (RAG)", 
       "Searches corporate handbook markdown files indexed in a vector store. The system reads documents dynamically, embeds queries, fetches matching segments, reranks them locally, and synthesizes answers."),
      ("Secure Mathematical Calculations", 
       "Resolves expressions securely via an AST parser tool without running dangerous generic scripts, allowing verified numeric calculation."),
      ("PII & Safety Compliance Scans", 
       "Scans response buffers before returning them. It intercepts, redacts, and masks sensitive data, such as emails, credit cards, and password hashes, returning sanitized blocks.")
    ]
    
    for title, desc in operations:
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(59, 130, 246)
        pdf.cell(0, 6, f'- {title}', 0, 1, 'L')
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(0, 5.5, desc)
        pdf.ln(3)
        
    pdf.add_page()
    
    # Section: Specialized Agents
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(24, 30, 45)
    pdf.cell(0, 10, '3. The 8 Specialized Agents', 0, 1, 'L')
    pdf.ln(4)
    
    agents_list = [
        ("Intent Router Agent", "Classifies user queries to decide execution paths (e.g. RAG, SQL, API, General, Unsafe) and intercepts SQL injections."),
        ("Task Planner Agent", "Constructs a checklist of required operations, revising the plan in case of execution anomalies."),
        ("SQL Database Agent", "Translates questions into read-only SQL SELECT queries and runs them against PostgreSQL."),
        ("Retrieval Agent", "Queries the Qdrant vector database and reranks the results via a Flashrank cross-encoder."),
        ("API Client Agent", "Triggers outbound integration web requests via MCP tools to fetch live details."),
        ("Reflection Agent (QA)", "Audits tool execution results. If errors occur, it loops back to the Planner with critiques."),
        ("Safety Compliance Agent", "Scans outputs, redacting credit cards, password hashes, and emails to preserve data privacy."),
        ("Report Compilation Agent", "Gathers all intermediate steps and compiles a final markdown report for the user.")
    ]
    
    for agent_name, agent_desc in agents_list:
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(139, 92, 246) # Accent Purple
        pdf.cell(0, 6, f'* {agent_name}', 0, 1, 'L')
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(0, 5.5, agent_desc)
        pdf.ln(3)

    pdf.add_page()
    
    # Section: Model Context Protocol
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(24, 30, 45)
    pdf.cell(0, 10, '4. Model Context Protocol (MCP) Integration', 0, 1, 'L')
    pdf.ln(4)
    
    mcp_text = (
        "The Model Context Protocol (MCP) is utilized to decouple agent core logic from tool execution. "
        "Rather than configuring tool scripts locally in the agent runtime, all tools (SQL, Retriever, Filesystem, "
        "Calculator, REST API, Memory) are exposed as standard endpoints by a dedicated MCP server.\n\n"
        "Endpoints and Call Lifecycle:\n"
        "1. GET /mcp/tools: Returns JSON tool schema definitions so agents understand required parameters.\n"
        "2. POST /mcp: Accepts argument schemas from agents, validates permissions, runs tools, and returns standard outputs.\n\n"
        "Local Fallback Design:\n"
        "To ensure high availability, if the gateway loses connection to the MCP microservice server, "
        "agents automatically default to local direct imports of the tool libraries to avoid downtime."
    )
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 5.5, mcp_text)
    pdf.ln(6)
    
    # Section: RAG Tech Stack
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(24, 30, 45)
    pdf.cell(0, 10, '5. RAG Technical Architecture', 0, 1, 'L')
    pdf.ln(4)
    
    rag_text = (
        "The Retrieval-Augmented Generation (RAG) system is built on a modern decoupled architecture:\n"
        "- Vector Store: Qdrant Database hosts vector collections containing segmented corporate manuals.\n"
        "- Indexing Pipeline: Python loaders segment markdown documents into semantic nodes, generate OpenAI embeddings (text-embedding-3-small), and upload points.\n"
        "- Query Processing: Combines cosine-similarity vector matches with an advanced local Flashrank reranker. Reranked contexts are fed to the LLM for precise citations, preventing hallucinations."
    )
    pdf.multi_cell(0, 5.5, rag_text)
    pdf.ln(6)
    
    # Section: Observability & Telemetry
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(24, 30, 45)
    pdf.cell(0, 10, '6. Observability & Monitoring Controls', 0, 1, 'L')
    pdf.ln(4)
    
    observability_text = (
        "Production runtime requires active health and latency tracking across the microservices:\n"
        "- Prometheus Integration: Exposes real-time endpoints collecting token counts, execution costs, retry loop intervals, and gateway HTTP counts.\n"
        "- Grafana Visualizations: Displays latency logs, total tokens consumed, cost tracking, and execution metrics on a clean dashboard.\n"
        "- LangSmith Tracing: Collects deep token traces and agent transition graphs, facilitating prompt and edge testing."
    )
    pdf.multi_cell(0, 5.5, observability_text)
    
    # Save PDF
    pdf.output(output_path)
    print(f"Generated PDF successfully at: {output_path}")

if __name__ == "__main__":
    out_dir = r"d:\projects\ai_eng"
    out_file = os.path.join(out_dir, "BIA_Project_Explanation.pdf")
    create_pdf(out_file)

import os
import sys
import subprocess

# Ensure fpdf library is installed
try:
    from fpdf import FPDF
except ImportError:
    print("[+] fpdf not found. Installing fpdf dynamically...")
    subprocess.run([sys.executable, "-m", "pip", "install", "fpdf"], check=True)
    from fpdf import FPDF

class BIAPresentationScriptPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(110, 110, 110)
            self.cell(0, 8, 'BIA Multi-Agent Operations Platform - Presentation Speaker Script', 0, 1, 'R')
            self.set_draw_color(220, 220, 220)
            self.line(10, 18, 200, 18)
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def add_section_header(self, text):
        self.set_font('Helvetica', 'B', 15)
        self.set_text_color(24, 30, 45) # Deep Slate Blue
        self.cell(0, 10, text, 0, 1, 'L')
        self.ln(3)

    def add_subsection_header(self, text, color=(59, 130, 246)):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(*color)
        self.cell(0, 8, text, 0, 1, 'L')
        self.ln(2)

    def add_body_paragraph(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 5.5, text)
        self.ln(4)

    def add_bullet_point(self, title, desc, bullet="* "):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(24, 30, 45)
        self.write(5.5, bullet + title + ": ")
        self.set_font('Helvetica', '', 10)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 5.5, desc)
        self.ln(2)

    def add_script_box(self, slide_num, title, visual, script_text):
        # Draw slide indicator
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(255, 255, 255)
        self.set_fill_color(59, 130, 246) # Blue header
        self.cell(0, 8, f" SLIDE {slide_num}: {title}", 0, 1, 'L', True)
        
        # Visual cues sub-box
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(100, 100, 100)
        self.set_fill_color(245, 247, 250) # Light grey background
        self.multi_cell(0, 5, f"[Visual Cue: {visual}]", 1, 'L', True)
        self.ln(2)

        # Speaking Script
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(37, 99, 235)
        self.cell(0, 5, "SPEAKER SCRIPT:", 0, 1, 'L')
        self.set_font('Helvetica', '', 9.5)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, script_text)
        self.ln(6)

def generate_script_pdf(output_path):
    pdf = BIAPresentationScriptPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # ----------------------------------------------------
    # COVER PAGE
    # ----------------------------------------------------
    pdf.add_page()
    pdf.ln(25)
    
    # Decorative primary colored bar
    pdf.set_fill_color(139, 92, 246) # Accent Purple
    pdf.rect(10, 48, 190, 6, 'F')
    
    pdf.ln(15)
    pdf.set_font('Helvetica', 'B', 26)
    pdf.set_text_color(24, 30, 45)
    pdf.cell(0, 12, 'BIA OPERATIONS PLATFORM', 0, 1, 'L')
    
    pdf.set_font('Helvetica', '', 16)
    pdf.set_text_color(100, 110, 130)
    pdf.cell(0, 10, 'Tomorrow\'s Presentation Speaker Script & Technical Reference', 0, 1, 'L')
    
    pdf.ln(10)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(139, 92, 246)
    pdf.cell(0, 6, 'SPEAKER NOTES & EXTENDED ARCHITECTURE SPECIFICATION', 0, 1, 'L')
    
    pdf.ln(50)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 5, 'Author & Presenter:', 0, 1, 'L')
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, 'Darshan Kamate (Principal AI Engineer & Software Architect)', 0, 1, 'L')
    
    pdf.ln(8)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 5, 'Main Technical Core:', 0, 1, 'L')
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, 'LangGraph Multi-Agent, RAG, Qdrant Vector, MCP Tool Server, PostgreSQL, Ragas Quality Evaluations', 0, 1, 'L')
    
    pdf.ln(8)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 5, 'Presentation Date:', 0, 1, 'L')
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, 'July 18, 2026', 0, 1, 'L')
    
    # ----------------------------------------------------
    # SECTION 1: INTRODUCTION & OVERVIEW
    # ----------------------------------------------------
    pdf.add_page()
    pdf.add_section_header("Part 1: Presentation Structure & Timing")
    pdf.add_body_paragraph(
        "This speaker notes document is structured to provide an easy-to-follow guide for tomorrow's presentation. "
        "The presentation is divided into a slide-by-slide verbal script corresponding to the 'BIA_Project_Explanation.pdf' "
        "manual, followed by deep-dive technical scripts describing the implementation of the RAG pipeline, LangGraph "
        "agent coordination, SQL auto-generation, Model Context Protocol (MCP) servers, and PostgreSQL configurations."
    )
    
    pdf.add_subsection_header("Timing & Delivery Strategy (Total: 15 Minutes)")
    pdf.add_bullet_point("Slide 1 (1 Min)", "Introduce yourself, the platform name (BIA Platform), and the core mission: bridging natural language prompts to secure enterprise transactions.")
    pdf.add_bullet_point("Slide 2 (3 Mins)", "Explain the four core capabilities. Emphasize read-only SQL queries, semantic RAG search, secure math using AST parsing, and PII/Safety scrubbing.")
    pdf.add_bullet_point("Slide 3 (4 Mins)", "Deep dive into the 8 specialized agents and how they coordinate. Highlight how routing, planning, and parallel worker executions operate statefully.")
    pdf.add_bullet_point("Slide 4 (3 Mins)", "Explain the decoupling using the Model Context Protocol (MCP), Qdrant vector retrieval architecture, and the Prometheus/Grafana/LangSmith observability suite.")
    pdf.add_bullet_point("Technical Q&A (4 Mins)", "Prepare to answer details about Ragas evaluations, SQL generation validation logic, and PostgreSQL database seeding.")

    # ----------------------------------------------------
    # SECTION 2: SLIDE-BY-SLIDE SCRIPTS
    # ----------------------------------------------------
    pdf.add_page()
    pdf.add_section_header("Part 2: Slide-by-Slide Speaker Scripts")

    pdf.add_script_box(
        "1", "BIA Platform Title Slide",
        "Display Cover slide. Point out your name, date, and technology stack keywords listed on page 1.",
        "Good morning everyone, and welcome to this technical walkthrough of the BIA Platform. "
        "Today, I am proud to share with you an enterprise-grade, stateful, and observable multi-agent AI system. "
        "As systems scale, managing database reads, parsing compliance manuals, and running integrations securely becomes a major challenge. "
        "The BIA Platform is our solution: a microservice-first system orchestrated by LangGraph that handles database operations, "
        "retrieval-augmented generation (or RAG), and automated data sanitization under strict role-based access control. "
        "Let's move into our capabilities."
    )

    pdf.add_script_box(
        "2", "Executive System Introduction & Core Capabilities",
        "Refer to page 2. Call out the four main points: SQL Queries, RAG Search, Secure Math, and PII Scans.",
        "Our platform is built on four core capabilities. "
        "First, Structured SQL Queries. Instead of manually writing queries, users can ask questions in plain English. The platform maps database schema structures, joins tables dynamically, and generates read-only SQL SELECT queries. "
        "Second, Unstructured Policy Search. This is our hybrid RAG pipeline. It reads markdown policies, indices them in Qdrant, and retrieves matching contexts with a Flashrank reranker. "
        "Third, Secure Mathematical Calculations. We bypass raw code execution by using an abstract syntax tree parser tool to calculate numeric values safely. "
        "Finally, PII & Safety Compliance. We run automatic scans to redact credit cards, email addresses, and password hashes from response streams, ensuring corporate compliance."
    )

    pdf.add_page()
    pdf.add_script_box(
        "3", "The 8 Specialized Agents Grid",
        "Refer to page 3. Walk the audience through the routing, planning, execution, and reflection cycle.",
        "At the core of BIA is our agent grid, orchestrated via LangGraph. Instead of a single LLM trying to do everything, we divide labor among 8 specialized agents. "
        "1. The Router Agent: Classifies the query intent, intercepts prompt injections, and applies role-based rules. "
        "2. The Task Planner Agent: Breaks down complex queries into a structured checklist. "
        "3. The SQL Agent: Translates questions into Postgres SELECT queries. "
        "4. The Retrieval Agent: Executes semantic vector lookups inside Qdrant. "
        "5. The API Agent: Hits system endpoints using standard REST tools. "
        "6. The Reflection Agent: Audits intermediate execution outputs. If a DB error is detected, it loops back to the Planner with critiques (up to 3 times). "
        "7. The Safety Agent: Redacts PII records from responses. "
        "8. The Report Agent: Synthesizes all intermediate steps into a clean markdown document for the client. "
        "This multi-agent coordination ensures that the system is self-correcting and secure."
    )

    pdf.add_script_box(
        "4", "MCP Tool Integration, RAG Architecture, & Observability",
        "Refer to page 4. Discuss tool decoupling (MCP), Qdrant vector structures, and Grafana monitoring panels.",
        "Let's talk infrastructure. First, we decouple our agent logic from tool execution using the Model Context Protocol (MCP) server. "
        "Our agents query tool schemas via /mcp/tools and trigger tools using POST requests to /mcp. This means if a tool breaks, the agent runtime stays healthy, and we have a local import fallback if the server goes offline. "
        "For RAG, we use Qdrant for vector retrieval, text-embedding-3-small for indexing, and local Flashrank rerankers to pull highly precise policy paragraphs. "
        "Lastly, we track everything in real-time. Prometheus scrapes API metrics, Grafana visualizes token costs and endpoint latencies, and LangSmith traces our agent transition steps to help developers test prompts. "
        "Now let's examine the code architecture behind these blocks."
    )

    # ----------------------------------------------------
    # SECTION 3: TECHNICAL DEEP-DIVES
    # ----------------------------------------------------
    pdf.add_page()
    pdf.add_section_header("Part 3: Extended Technical Deep-Dives")
    
    # 1. RAG Deep Dive
    pdf.add_subsection_header("1. Deep-Dive on RAG Architecture & Quality Evaluation")
    pdf.add_body_paragraph(
        "Our RAG pipeline is implemented in the 'rag-service' microservice. Document ingestion follows a robust path. "
        "Admin or Manager accounts upload markdown files via the API Gateway. The RAG service receives the file, and "
        "loader.py loads the raw content. Next, chunker.py uses LangChain's 'RecursiveCharacterTextSplitter' with a chunk size "
        "of 1000 characters and a chunk overlap of 150 characters. This preserves context boundaries (like paragraph ends and titles) "
        "without splitting sentences mid-thought."
    )
    pdf.add_body_paragraph(
        "For embeddings, we call OpenAI's 'text-embedding-3-small', generating 1536-dimensional vectors. These vectors are "
        "uploaded in batches to Qdrant collections. During the retrieval phase, the query is embedded and we execute a cosine similarity "
        "search in Qdrant (retrieving top-k = 10 chunks). To filter out noise and improve response precision, we run these chunks through "
        "Flashrank's local cross-encoder reranker ('ms-marco-MiniLM-L-6-v2'), returning the top-4 most relevant context snippets."
    )
    pdf.add_body_paragraph(
        "To guarantee response quality, we run automated tests in 'tests/test_rag_evaluation.py' scoring the system across four "
        "Ragas metrics: Faithfulness (checking if answers are derived strictly from context), Answer Relevancy (ensuring answers address "
        "the query), Context Precision (ensuring relevant chunks are ranked high), and Context Recall (measuring retrieved coverage "
        "against reference answers). The script features a Live Mode (calling OpenAI models to grade metrics) and a local "
        "Simulated Mode that calculates word overlap and context similarity locally if no API key is available, outputting results to "
        "'evaluation_report.html' and 'evaluation_report.json'."
    )

    # 2. Agentic Lifecycle
    pdf.add_page()
    pdf.add_subsection_header("2. LangGraph StateGraph & Execution Lifecycle")
    pdf.add_body_paragraph(
        "Our agents are orchestrated statefully using LangGraph's StateGraph, defined in 'agents/graph.py'. The state "
        "variable (defined as AgentState in 'state/state.py') tracks history, active query parameters, the current plan steps, "
        "retrieved contexts, SQL statements, and API results. When a client submits a message, the graph triggers a sequential execution."
    )
    pdf.add_body_paragraph(
        "The graph begins at the Router node, which runs conditional edges. If a query is unsafe, it bypasses execution and routes "
        "directly to the Safety node, then the Report node. If the query is a simple greeting, it jumps straight to the Report node. "
        "For operational queries, it routes to the Planner. The Planner generates a step checklist, saving a checkpointer state "
        "in Redis. The graph then branches out (parallel fan-out) to execute RAG, SQL, and API worker nodes in parallel."
    )
    pdf.add_body_paragraph(
        "These worker outputs synchronize at the Merge node (fan-in). The merged state is evaluated by the Reflection node. "
        "If Reflection detects a missing column or empty context, it increments the retry counter and loops back to the Planner "
        "for plan revisions. Otherwise, it routes to the Safety node for PII scrubbing and outputs the final Markdown via the Report agent."
    )

    # 3. SQL Generator Mechanics
    pdf.add_subsection_header("3. SQL Query Generation, Sanitization, & Security")
    pdf.add_body_paragraph(
        "The SQL Agent ('agents/sql.py') is tasked with translating user questions into valid SQL SELECT statements. "
        "First, it maps table definitions. The database schemas are loaded dynamically so the LLM understands table relations "
        "(e.g., how orders link to customers). However, letting an LLM generate SQL presents extreme security risks."
    )
    pdf.add_body_paragraph(
        "To mitigate this, the SQL Agent and the MCP SQL tool apply strict security isolation rules. First, queries must "
        "strictly contain 'SELECT' statements. If the query text contains writing operations such as 'INSERT', 'UPDATE', 'DELETE', "
        "'DROP', or 'ALTER', the execution is intercepted and blocked. Second, we apply database-level read-only connection pooling parameters. "
        "The database connections are managed via SQLAlchemy connection pooling with a pool size of 10 and max overflow of 20, "
        "with auto-recycle parameters to clean idle connections. This ensures high availability and blocks write privileges "
        "for the agent role, preventing any data modifications."
    )

    # 4. Model Context Protocol (MCP) in Action
    pdf.add_page()
    pdf.add_subsection_header("4. Model Context Protocol (MCP) Integration & Call Lifecycle")
    pdf.add_body_paragraph(
        "Rather than having agents execute tools locally in their runtime environment, the BIA Platform decouples tool execution "
        "using the Model Context Protocol (MCP). The tools are registered inside 'mcp-server/mcp_app.py'. This microservice "
        "runs on port 8080 and exposes tool capabilities to our LangGraph nodes."
    )
    pdf.add_body_paragraph(
        "The call lifecycle is simple: 1. The Gateway calls GET /mcp/tools, which returns JSON metadata of all tools (e.g. calculator, "
        "sql_query, retriever). The LLM reads these tool schemas to understand required parameters. 2. When an agent decides to run "
        "a tool, it posts arguments to POST /mcp. The MCP server validates the arguments, runs the script (like hitting Postgres or "
        "calling Qdrant), and returns a standard JSON result. If the MCP microservice is down, the agents fall back to local direct imports "
        "of the tools libraries to avoid system downtime."
    )

    # 5. PostgreSQL Database Connection
    pdf.add_subsection_header("5. Connecting PostgreSQL & SQLAlchemy with the Project")
    pdf.add_body_paragraph(
        "Our connection to PostgreSQL is managed under the 'postgres' directory. In 'postgres/database.py', we initialize the "
        "SQLAlchemy engine using create_engine with pool_size=10, max_overflow=20, and pool_recycle=1800 to prevent stale connections. "
        "A context manager db_session() is defined to manage sessions locally. It guarantees transaction isolation by automatically "
        "committing on success, rolling back on exception, and closing the connection in the finally block."
    )
    pdf.add_body_paragraph(
        "In 'postgres/models.py', we map tables using SQLAlchemy's Declarative Base. We define schemas for Department, Employee, "
        "User, Customer, Product, Inventory, Order, and SupportTicket. In 'postgres/repositories.py', we implement a Generic CRUD "
        "repository pattern (BaseRepository) to perform queries cleanly. Finally, 'postgres/service.py' manages database initialization "
        "and data importing. During setup, it reads local CSV files under 'data/database' and imports rows sequentially into Postgres "
        "while resolving relational constraints, establishing a complete mock transactional store for presentation testing."
    )

    # Save PDF
    pdf.output(output_path)
    print(f"Generated PDF successfully at: {output_path}")

if __name__ == "__main__":
    out_dir = r"d:\projects\ai_eng"
    out_file = os.path.join(out_dir, "BIA_Presentation_Script.pdf")
    generate_script_pdf(out_file)

import os
import sys
import argparse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Ensure parent directory is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)

from config import settings
from postgres.database import Base, db_session
from postgres.service import init_db, seed_db_from_csv

def test_postgres_connection() -> bool:
    """Check if the configured PostgreSQL database is reachable."""
    try:
        engine = create_engine(settings.db.connection_url, connect_args={"connect_timeout": 2})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

def run_query(query: str):
    print("====================================================")
    print("Darshan_AI_Engineer_Ops SQL Execution & Test Utility")
    print("====================================================")
    print(f"SQL Query to execute: \n{query}\n")

    # 1. Strict read-only query check (similar to SQLTool guardrail)
    forbidden_keywords = {"insert", "update", "delete", "drop", "alter", "create", "truncate", "replace"}
    cleaned_query = query.strip().lower()
    tokens = set(cleaned_query.split())
    if forbidden_keywords.intersection(tokens):
        print("Error: Write or schema-modifying queries are strictly prohibited.", file=sys.stderr)
        return

    # 2. Check DB connection
    postgres_active = test_postgres_connection()
    
    if postgres_active:
        print("Connected to PostgreSQL database successfully.")
        try:
            with db_session() as session:
                result = session.execute(text(query))
                cols = list(result.keys())
                rows = result.fetchall()
        except Exception as e:
            print(f"PostgreSQL Execution Error: {e}", file=sys.stderr)
            return
    else:
        print("Warning: PostgreSQL could not be reached (Docker container may not be running).")
        print("Falling back to an in-memory SQLite database seeded with mock CSV data...")
        
        try:
            # Create SQLite memory engine and schema
            sqlite_engine = create_engine("sqlite:///:memory:")
            Base.metadata.create_all(bind=sqlite_engine)
            
            # Setup session and seed
            SessionLocal = sessionmaker(bind=sqlite_engine)
            session = SessionLocal()
            
            data_dir = os.path.join(root_dir, "data", "database")
            seed_db_from_csv(session, data_dir)
            session.commit()
            
            # Run the query
            result = session.execute(text(query))
            cols = list(result.keys())
            rows = result.fetchall()
            session.close()
            
        except Exception as e:
            print(f"SQLite/Fallback Execution Error: {e}", file=sys.stderr)
            return

    # 3. Format and print the output
    if not rows:
        print("\nQuery executed successfully. 0 rows returned.")
        return
        
    print(f"\nResults ({len(rows)} rows):")
    # Determine column widths for basic printing
    widths = [len(col) for col in cols]
    for row in rows:
        for idx, val in enumerate(row):
            widths[idx] = max(widths[idx], len(str(val)))
            
    header_line = " | ".join(col.ljust(widths[idx]) for idx, col in enumerate(cols))
    divider_line = "-+-".join("-" * widths[idx] for idx in range(len(cols)))
    
    print(header_line)
    print(divider_line)
    for row in rows:
        print(" | ".join(str(val).ljust(widths[idx]) for idx, val in enumerate(row)))
    print("====================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test and execute simple SQL queries on the project database.")
    parser.add_argument(
        "query", 
        type=str, 
        nargs="?", 
        default="SELECT * FROM departments LIMIT 5;",
        help="The read-only SQL query to run. Default is 'SELECT * FROM departments LIMIT 5;'"
    )
    args = parser.parse_args()
    run_query(args.query)

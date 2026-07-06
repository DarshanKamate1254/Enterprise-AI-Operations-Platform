from typing import List, Dict, Any, Tuple
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session


class SQLTool:
    """
    SQL Query Tool for Database Inspection and Read-Only Query Execution.
    Uses Dependency Injection to receive database Session objects.
    """
    def __init__(self, session: Session):
        self.session = session

    def execute_query(self, sql_query: str) -> Tuple[List[str], List[Tuple[Any, ...]]]:
        """
        Executes a raw SQL query.
        Enforces read-only operations to protect against database writes.
        Returns:
            Tuple of (columns, rows)
        """
        # Strict read-only query check
        forbidden_keywords = {"insert", "update", "delete", "drop", "alter", "create", "truncate", "replace"}
        cleaned_query = sql_query.strip().lower()
        
        # Tokenize query to check for forbidden keywords
        tokens = set(cleaned_query.split())
        if forbidden_keywords.intersection(tokens):
            raise PermissionError("Write or schema-modifying queries are strictly prohibited on this endpoint.")

        # Run query using the injected session
        result = self.session.execute(text(sql_query))
        
        # Extract columns and rows
        columns = list(result.keys())
        rows = result.fetchall()
        return columns, rows

    def get_schema(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Inspects the database schema and returns all table names, columns, and types.
        """
        inspector = inspect(self.session.bind)
        schema_info = {}
        
        for table_name in inspector.get_table_names():
            columns_info = []
            for col in inspector.get_columns(table_name):
                columns_info.append({
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": "YES" if col["nullable"] else "NO"
                })
            schema_info[table_name] = columns_info
            
        return schema_info

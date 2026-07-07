import re
from typing import List, Set


def detect_prompt_injection(query: str) -> bool:
    """
    Scans incoming queries for instruction overrides, system constraints escapes,
    or jailbreak payloads.
    """
    injection_patterns = [
        r"ignore\s+(?:previous|all)\s+instructions",
        r"system\s+prompt\s*(?:override|bypass|reveal)",
        r"you\s+are\s+now\s+a\s+different\s+ai",
        r"acting\s+as\s+a\s+dan",
        r"jailbreak",
        r"override\s+security",
        r"forget\s+rules",
        r"do\s+anything\s+now"
    ]
    
    cleaned_query = query.lower()
    for pattern in injection_patterns:
        if re.search(pattern, cleaned_query):
            return True
            
    return False


def detect_pii_and_redact(text: str) -> str:
    """
    Identifies sensitive numbers (credit cards), emails, and cryptographic password hashes,
    redacting them with [REDACTED].
    """
    # 1. Credit card numbers (standard 16 digit groupings)
    card_pattern = r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"
    text = re.sub(card_pattern, "[REDACTED_CREDIT_CARD]", text)
    
    # 2. Cryptographic password hashes (typical Bcrypt standard formats)
    bcrypt_pattern = r"\$2[abxy]\$\d{2}\$[./A-Za-z0-9]{53}"
    text = re.sub(bcrypt_pattern, "[REDACTED_PASSWORD_HASH]", text)
    
    # 3. Emails
    email_pattern = r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-_]+\.[a-zA-Z0-9-._]+\b"
    text = re.sub(email_pattern, "[REDACTED_EMAIL]", text)
    
    return text


def validate_sql_syntax_and_whitelist(query: str) -> bool:
    """
    Validates that a generated SQL query targets only whitelisted tables
    and consists strictly of read-only SELECT clauses.
    """
    cleaned = query.strip().lower()
    
    # Strictly SELECT read-only checks
    forbidden_keywords = {"insert", "update", "delete", "drop", "alter", "create", "truncate", "replace"}
    tokens = set(cleaned.replace("(", " ").replace(")", " ").replace(";", " ").split())
    
    if forbidden_keywords.intersection(tokens):
        return False
        
    # Whitelisted database tables
    whitelist_tables = {
        "departments",
        "employees",
        "users",
        "customers",
        "products",
        "inventory",
        "orders",
        "support_tickets"
    }
    
    # Identify tables in query using simple token search after FROM or JOIN
    found_tables = set()
    words = cleaned.replace("(", " ").replace(")", " ").replace(";", " ").split()
    
    for idx, word in enumerate(words):
        if word in ("from", "join") and idx + 1 < len(words):
            table_token = words[idx + 1].strip("`'\"")
            # Strip schemas if any (e.g. public.employees)
            if "." in table_token:
                table_token = table_token.split(".")[-1]
            found_tables.add(table_token)
            
    # Verify all identified tables are in whitelist
    if found_tables and not found_tables.issubset(whitelist_tables):
        return False
        
    return True


def validate_role_query_access(role: str, query: str) -> bool:
    """
    Role-Based Query access validator.
    Prevents basic 'User' roles from querying sensitive salary, password, or administrative user details.
    """
    role = role.strip().capitalize() if role else "User"
    cleaned = query.strip().lower()
    
    # If the user is a basic 'User', block access to sensitive table components
    if role == "User":
        sensitive_tokens = {"salary", "password_hash", "users"}
        tokens = set(cleaned.replace("(", " ").replace(")", " ").replace(";", " ").replace(",", " ").split())
        
        if sensitive_tokens.intersection(tokens):
            return False
            
    return True

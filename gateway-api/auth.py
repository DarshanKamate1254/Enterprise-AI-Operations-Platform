import sys
import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import encode, decode, PyJWTError

from config import settings

# Setup JWT parameters
# Setup JWT parameters from settings
JWT_SECRET = settings.app.jwt_secret_key
ALGORITHM = settings.app.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.app.access_token_expire_minutes

security_scheme = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a secure JWT access token containing user identity and role.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> Dict[str, Any]:
    """
    Dependency that decodes the incoming bearer token and extracts user data.
    """
    token = credentials.credentials
    try:
        payload = decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        user_id: int = payload.get("user_id")
        
        if username is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials: Sub/Role missing in token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"username": username, "role": role, "user_id": user_id}
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials: Token signature invalid or expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )


class RoleChecker:
    """
    Role verification dependency checker for RBAC route protection.
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_role = current_user.get("role")
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access Denied: User role '{user_role}' is not authorized to access this resource."
            )
        return current_user

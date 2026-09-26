"""
JWT Authentication System for ReturnIQ
Multi-tenant authentication with database-backed users and demo mode
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
import jwt
import os
from pydantic import BaseModel
import bcrypt
import uuid

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    import warnings
    warnings.warn("JWT_SECRET_KEY not set! Using insecure default. Set JWT_SECRET_KEY environment variable in production.")
    SECRET_KEY = "dev-secret-key-change-in-production"

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

# ============================================================================
# Models
# ============================================================================

class TokenData(BaseModel):
    """JWT Token payload - Multi-tenant aware"""
    user_id: str
    username: str
    email: str
    role: str = "analyst"
    tenant_id: str = None

class Token(BaseModel):
    """API response for token generation"""
    access_token: str
    token_type: str = "bearer"
    user_id: str = None
    email: str = None
    role: str = None
    tenant_id: str = None

class User(BaseModel):
    """User object from token"""
    user_id: str
    username: str
    email: str
    role: str
    tenant_id: str = None

# ============================================================================
# Password Hashing
# ============================================================================

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False

# ============================================================================
# Demo Users (for testing and demos)
# ============================================================================

DEMO_TENANT_ID = str(uuid.UUID("00000000-0000-0000-0000-000000000001"))
DEMO_USERS = {
    "demo": {
        "user_id": str(uuid.UUID("10000000-0000-0000-0000-000000000001")),
        "username": "demo",
        "email": "demo@returniq.com",
        "password": "demo-password",
        "role": "admin",
        "tenant_id": DEMO_TENANT_ID,
        "first_name": "Demo",
        "last_name": "User",
    },
    "analyst": {
        "user_id": str(uuid.UUID("10000000-0000-0000-0000-000000000002")),
        "username": "analyst",
        "email": "analyst@returniq.com",
        "password": "analyst-password",
        "role": "analyst",
        "tenant_id": DEMO_TENANT_ID,
        "first_name": "Analyst",
        "last_name": "User",
    },
    "manager": {
        "user_id": str(uuid.UUID("10000000-0000-0000-0000-000000000003")),
        "username": "manager",
        "email": "manager@returniq.com",
        "password": "manager-password",
        "role": "manager",
        "tenant_id": DEMO_TENANT_ID,
        "first_name": "Manager",
        "last_name": "User",
    },
    "support": {
        "user_id": str(uuid.UUID("10000000-0000-0000-0000-000000000004")),
        "username": "support",
        "email": "support@returniq.com",
        "password": "support-password",
        "role": "support",
        "tenant_id": DEMO_TENANT_ID,
        "first_name": "Support",
        "last_name": "User",
    }
}

# ============================================================================
# Token Functions
# ============================================================================

def create_access_token(data: TokenData, expires_delta: Optional[timedelta] = None) -> str:
    """Generate JWT access token with multi-tenant support"""
    to_encode = {
        "user_id": data.user_id,
        "username": data.username,
        "email": data.email,
        "role": data.role,
        "tenant_id": data.tenant_id,
    }

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(authorization: Optional[str] = Header(None)) -> TokenData:
    """Verify JWT token and return token data with tenant info"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = parts[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        username: str = payload.get("username")
        email: str = payload.get("email")
        role: str = payload.get("role", "analyst")
        tenant_id: str = payload.get("tenant_id")

        if user_id is None or tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return TokenData(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            tenant_id=tenant_id
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(token_data: TokenData = Depends(verify_token)) -> User:
    """Get current authenticated user with tenant info"""
    return User(
        user_id=token_data.user_id,
        username=token_data.username,
        email=token_data.email,
        role=token_data.role,
        tenant_id=token_data.tenant_id
    )

# ============================================================================
# Authentication Functions
# ============================================================================

def authenticate_user_demo(username: str, password: str) -> Optional[TokenData]:
    """Authenticate user against demo users (for development)"""
    if not DEMO_MODE:
        return None

    user = DEMO_USERS.get(username)
    if not user or user["password"] != password:
        return None

    return TokenData(
        user_id=user["user_id"],
        username=user["username"],
        email=user["email"],
        role=user["role"],
        tenant_id=user["tenant_id"]
    )

def authenticate_user_database(email: str, password: str, db_session) -> Optional[TokenData]:
    """Authenticate user against database (production)"""
    from .database.models import User as UserModel

    user = db_session.query(UserModel).filter(UserModel.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return None

    return TokenData(
        user_id=str(user.id),
        username=user.email.split("@")[0],
        email=user.email,
        role=user.role,
        tenant_id=str(user.tenant_id)
    )

def authenticate_user(username_or_email: str, password: str, db_session=None) -> Optional[TokenData]:
    """Authenticate user - tries demo first, then database"""
    # Try demo authentication if enabled
    token_data = authenticate_user_demo(username_or_email, password)
    if token_data:
        return token_data

    # Try database authentication
    if db_session:
        token_data = authenticate_user_database(username_or_email, password, db_session)
        if token_data:
            return token_data

    return None

def create_demo_token() -> str:
    """Create demo token for quick testing"""
    token_data = TokenData(
        user_id=DEMO_USERS["demo"]["user_id"],
        username="demo",
        email="demo@returniq.com",
        role="admin",
        tenant_id=DEMO_TENANT_ID
    )
    return create_access_token(token_data)

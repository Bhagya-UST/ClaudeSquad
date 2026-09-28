"""
Dependency Injection for FastAPI routes
Provides current user, tenant, and permissions
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from .auth import verify_token, TokenData
from .database.models import User, Tenant
from .database.db import Database
from .auth_rbac import get_role_permissions
import uuid

db = Database()

# Demo/fallback user for demo mode
DEMO_USER = type('User', (), {
    'id': uuid.uuid4(),
    'user_id': 'demo_user',
    'tenant_id': uuid.uuid4(),
    'email': 'demo@example.com',
    'role': 'analyst',
    'is_active': True
})()

DEMO_TENANT = type('Tenant', (), {
    'id': DEMO_USER.tenant_id,
    'name': 'Demo Tenant',
    'slug': 'demo'
})()

async def get_current_tenant(token_data: Optional[TokenData] = None) -> Tenant:
    """Get current tenant from JWT token or return demo tenant"""
    if not token_data:
        return DEMO_TENANT

    if not token_data.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant information not found in token"
        )

    session = db.get_session()
    tenant = session.query(Tenant).filter(Tenant.id == token_data.tenant_id).first()
    session.close()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant not found"
        )

    return tenant

async def get_current_user(token_data: Optional[TokenData] = None) -> User:
    """Get current user from JWT token or return demo user"""
    if not token_data:
        return DEMO_USER

    session = db.get_session()
    user = session.query(User).filter(
        User.id == token_data.user_id,
        User.tenant_id == token_data.tenant_id
    ).first()
    session.close()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user

async def get_user_permissions(user: User = Depends(get_current_user)) -> list[str]:
    """Get permissions for current user based on role"""
    permissions = get_role_permissions(user.role)
    return [p.value for p in permissions]

async def require_permission(required_permission: str):
    """Factory to create permission requirement"""
    async def _require_permission(permissions: list[str] = Depends(get_user_permissions)):
        if required_permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {required_permission} required"
            )
        return True
    return _require_permission

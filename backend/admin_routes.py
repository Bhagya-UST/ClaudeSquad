"""
Admin Routes for ReturnIQ
User management, role management, and tenant settings
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from typing import List
import uuid
from datetime import datetime

from .database.models import User, UserRole, Tenant, AuditLog
from .database.db import Database
from .dependencies import get_current_user, get_current_tenant, get_user_permissions
from .auth_rbac import Permission
from .auth import hash_password

router = APIRouter(prefix="/api/admin", tags=["admin"])
db = Database()

# ============================================================================
# Request/Response Models
# ============================================================================

class UserCreate(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    role: str = "analyst"

class UserUpdate(BaseModel):
    first_name: str = None
    last_name: str = None
    role: str = None

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: datetime = None

class RoleResponse(BaseModel):
    role: str
    permissions: dict

class TenantSettingsResponse(BaseModel):
    name: str
    slug: str
    metadata: dict

class TenantSettingsUpdate(BaseModel):
    name: str = None
    metadata: dict = None

class UsageMetrics(BaseModel):
    returns_processed: int
    api_calls: int
    team_members: int
    created_at: datetime

# ============================================================================
# User Management Endpoints
# ============================================================================

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_create: UserCreate,
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    permissions: List[str] = Depends(get_user_permissions)
):
    """Create a new user in the tenant"""
    if Permission.MANAGE_USERS.value not in permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    session = db.get_session()

    # Check if user already exists
    existing = session.query(User).filter(
        User.tenant_id == current_tenant.id,
        User.email == user_create.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )

    # Create new user
    new_user = User(
        id=uuid.uuid4(),
        tenant_id=current_tenant.id,
        email=user_create.email,
        password_hash=hash_password(user_create.password),
        first_name=user_create.first_name,
        last_name=user_create.last_name,
        role=user_create.role,
        is_active=True
    )

    session.add(new_user)
    session.commit()

    # Log audit
    audit_log = AuditLog(
        id=uuid.uuid4(),
        tenant_id=current_tenant.id,
        user_id=current_user.id,
        action="create_user",
        resource_type="user",
        resource_id=new_user.id,
        new_values={"email": new_user.email, "role": new_user.role},
        status="success"
    )
    session.add(audit_log)
    session.commit()
    session.close()

    return UserResponse(
        id=str(new_user.id),
        email=new_user.email,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        role=new_user.role,
        is_active=new_user.is_active,
        created_at=new_user.created_at
    )

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    permissions: List[str] = Depends(get_user_permissions),
    skip: int = 0,
    limit: int = 50
):
    """List all users in tenant"""
    if Permission.VIEW_USERS.value not in permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    session = db.get_session()
    users = session.query(User).filter(
        User.tenant_id == current_tenant.id
    ).offset(skip).limit(limit).all()
    session.close()

    return [
        UserResponse(
            id=str(u.id),
            email=u.email,
            first_name=u.first_name,
            last_name=u.last_name,
            role=u.role,
            is_active=u.is_active,
            created_at=u.created_at,
            last_login=u.last_login
        )
        for u in users
    ]

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    permissions: List[str] = Depends(get_user_permissions)
):
    """Update a user"""
    if Permission.MANAGE_USERS.value not in permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    session = db.get_session()
    user = session.query(User).filter(
        User.id == user_id,
        User.tenant_id == current_tenant.id
    ).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Store old values for audit
    old_values = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role
    }

    # Update fields
    if user_update.first_name:
        user.first_name = user_update.first_name
    if user_update.last_name:
        user.last_name = user_update.last_name
    if user_update.role:
        user.role = user_update.role

    session.commit()

    # Log audit
    audit_log = AuditLog(
        id=uuid.uuid4(),
        tenant_id=current_tenant.id,
        user_id=current_user.id,
        action="update_user",
        resource_type="user",
        resource_id=user.id,
        old_values=old_values,
        new_values=user_update.dict(exclude_unset=True),
        status="success"
    )
    session.add(audit_log)
    session.commit()
    session.close()

    return UserResponse(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login=user.last_login
    )

@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    permissions: List[str] = Depends(get_user_permissions)
):
    """Deactivate a user"""
    if Permission.MANAGE_USERS.value not in permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    session = db.get_session()
    user = session.query(User).filter(
        User.id == user_id,
        User.tenant_id == current_tenant.id
    ).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_active = False
    session.commit()

    # Log audit
    audit_log = AuditLog(
        id=uuid.uuid4(),
        tenant_id=current_tenant.id,
        user_id=current_user.id,
        action="deactivate_user",
        resource_type="user",
        resource_id=user.id,
        new_values={"is_active": False},
        status="success"
    )
    session.add(audit_log)
    session.commit()
    session.close()

    return {"status": "success", "message": "User deactivated"}

# ============================================================================
# Settings Endpoints
# ============================================================================

@router.get("/settings", response_model=TenantSettingsResponse)
async def get_settings(
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    permissions: List[str] = Depends(get_user_permissions)
):
    """Get tenant settings"""
    if Permission.VIEW_SETTINGS.value not in permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    return TenantSettingsResponse(
        name=current_tenant.name,
        slug=current_tenant.slug,
        metadata=current_tenant.metadata or {}
    )

@router.put("/settings", response_model=TenantSettingsResponse)
async def update_settings(
    settings_update: TenantSettingsUpdate,
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    permissions: List[str] = Depends(get_user_permissions)
):
    """Update tenant settings"""
    if Permission.MANAGE_SETTINGS.value not in permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    session = db.get_session()

    if settings_update.name:
        current_tenant.name = settings_update.name
    if settings_update.metadata:
        current_tenant.metadata = settings_update.metadata

    current_tenant.updated_at = datetime.utcnow()
    session.commit()
    session.close()

    return TenantSettingsResponse(
        name=current_tenant.name,
        slug=current_tenant.slug,
        metadata=current_tenant.metadata or {}
    )

# ============================================================================
# Audit Log Endpoints
# ============================================================================

@router.get("/audit-logs")
async def get_audit_logs(
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    permissions: List[str] = Depends(get_user_permissions),
    skip: int = 0,
    limit: int = 50,
    action: str = None
):
    """Get tenant audit logs"""
    if Permission.VIEW_AUDIT_LOGS.value not in permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    session = db.get_session()
    query = session.query(AuditLog).filter(AuditLog.tenant_id == current_tenant.id)

    if action:
        query = query.filter(AuditLog.action == action)

    logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    total = query.count()
    session.close()

    return {
        "status": "success",
        "data": [
            {
                "id": str(log.id),
                "user_id": str(log.user_id) if log.user_id else None,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": str(log.resource_id) if log.resource_id else None,
                "status": log.status,
                "timestamp": log.timestamp.isoformat(),
                "old_values": log.old_values,
                "new_values": log.new_values
            }
            for log in logs
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    }

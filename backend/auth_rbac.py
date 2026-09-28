"""
Role-Based Access Control (RBAC) System for ReturnIQ
Handles permissions, roles, and access control
"""

from enum import Enum
from typing import List, Set
from fastapi import HTTPException, status

class Permission(str, Enum):
    """Core permissions for ReturnIQ"""
    # Return management
    VIEW_RETURNS = "view_returns"
    CREATE_RETURN = "create_return"
    EDIT_RETURN = "edit_return"
    DELETE_RETURN = "delete_return"

    # Classification & Analysis
    VIEW_CLASSIFICATIONS = "view_classifications"
    EDIT_CLASSIFICATIONS = "edit_classifications"

    # Trends & Patterns
    VIEW_TRENDS = "view_trends"
    MANAGE_TRENDS = "manage_trends"

    # Recommendations
    VIEW_RECOMMENDATIONS = "view_recommendations"
    CREATE_RECOMMENDATIONS = "create_recommendations"
    APPROVE_RECOMMENDATIONS = "approve_recommendations"
    REJECT_RECOMMENDATIONS = "reject_recommendations"
    IMPLEMENT_RECOMMENDATIONS = "implement_recommendations"

    # Emotional Intelligence & Interventions
    VIEW_EI = "view_ei"
    MANAGE_INTERVENTIONS = "manage_interventions"

    # Admin/Settings
    VIEW_USERS = "view_users"
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    VIEW_SETTINGS = "view_settings"
    MANAGE_SETTINGS = "manage_settings"

    # Audit & Compliance
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_AUDIT_LOGS = "manage_audit_logs"

    # Admin Dashboard
    VIEW_ADMIN_DASHBOARD = "view_admin_dashboard"
    VIEW_USAGE_METRICS = "view_usage_metrics"
    MANAGE_TENANT_SETTINGS = "manage_tenant_settings"

class Role(str, Enum):
    """Predefined roles for ReturnIQ"""
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    SUPPORT = "support"
    VIEWER = "viewer"

# Default permissions per role
ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        # Full access
        Permission.VIEW_RETURNS,
        Permission.CREATE_RETURN,
        Permission.EDIT_RETURN,
        Permission.DELETE_RETURN,
        Permission.VIEW_CLASSIFICATIONS,
        Permission.EDIT_CLASSIFICATIONS,
        Permission.VIEW_TRENDS,
        Permission.MANAGE_TRENDS,
        Permission.VIEW_RECOMMENDATIONS,
        Permission.CREATE_RECOMMENDATIONS,
        Permission.APPROVE_RECOMMENDATIONS,
        Permission.REJECT_RECOMMENDATIONS,
        Permission.IMPLEMENT_RECOMMENDATIONS,
        Permission.VIEW_EI,
        Permission.MANAGE_INTERVENTIONS,
        Permission.VIEW_USERS,
        Permission.MANAGE_USERS,
        Permission.MANAGE_ROLES,
        Permission.VIEW_SETTINGS,
        Permission.MANAGE_SETTINGS,
        Permission.VIEW_AUDIT_LOGS,
        Permission.MANAGE_AUDIT_LOGS,
        Permission.VIEW_ADMIN_DASHBOARD,
        Permission.VIEW_USAGE_METRICS,
        Permission.MANAGE_TENANT_SETTINGS,
    },
    Role.MANAGER: {
        # Can view and approve actions
        Permission.VIEW_RETURNS,
        Permission.EDIT_RETURN,
        Permission.VIEW_CLASSIFICATIONS,
        Permission.VIEW_TRENDS,
        Permission.VIEW_RECOMMENDATIONS,
        Permission.APPROVE_RECOMMENDATIONS,
        Permission.REJECT_RECOMMENDATIONS,
        Permission.IMPLEMENT_RECOMMENDATIONS,
        Permission.VIEW_EI,
        Permission.MANAGE_INTERVENTIONS,
        Permission.VIEW_USERS,
        Permission.VIEW_SETTINGS,
        Permission.VIEW_AUDIT_LOGS,
        Permission.VIEW_ADMIN_DASHBOARD,
        Permission.VIEW_USAGE_METRICS,
    },
    Role.ANALYST: {
        # Can view and interact with analysis
        Permission.VIEW_RETURNS,
        Permission.CREATE_RETURN,
        Permission.VIEW_CLASSIFICATIONS,
        Permission.VIEW_TRENDS,
        Permission.VIEW_RECOMMENDATIONS,
        Permission.VIEW_EI,
        Permission.VIEW_AUDIT_LOGS,
    },
    Role.SUPPORT: {
        # Customer service representative - limited access
        Permission.VIEW_RETURNS,
        Permission.CREATE_RETURN,
        Permission.VIEW_CLASSIFICATIONS,
        Permission.VIEW_EI,
        Permission.MANAGE_INTERVENTIONS,
    },
    Role.VIEWER: {
        # Read-only access
        Permission.VIEW_RETURNS,
        Permission.VIEW_CLASSIFICATIONS,
        Permission.VIEW_TRENDS,
        Permission.VIEW_RECOMMENDATIONS,
        Permission.VIEW_EI,
    },
}

def get_role_permissions(role: str) -> Set[Permission]:
    """Get permissions for a role"""
    try:
        role_enum = Role(role)
        return ROLE_PERMISSIONS.get(role_enum, set())
    except ValueError:
        return set()

def has_permission(user_permissions: List[str], required_permission: Permission) -> bool:
    """Check if user has required permission"""
    return required_permission.value in user_permissions

def check_permission(user_permissions: List[str], required_permission: Permission) -> None:
    """Raise 403 if user doesn't have permission"""
    if not has_permission(user_permissions, required_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: {required_permission.value} required"
        )

def require_permission(*permissions: Permission):
    """Decorator to require one or more permissions"""
    def decorator(func):
        async def wrapper(*args, user_permissions: List[str] = None, **kwargs):
            if not user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User permissions not found"
                )

            has_any = any(
                has_permission(user_permissions, perm)
                for perm in permissions
            )

            if not has_any:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: one of {[p.value for p in permissions]} required"
                )

            return await func(*args, user_permissions=user_permissions, **kwargs)

        return wrapper
    return decorator

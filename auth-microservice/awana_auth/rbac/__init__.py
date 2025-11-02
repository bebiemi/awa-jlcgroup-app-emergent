"""Role-Based Access Control (RBAC) system"""

from .models import Role, Permission, UserRole
from .decorators import require_role, require_permission, require_any_role
from .manager import RBACManager

__all__ = [
    "Role",
    "Permission",
    "UserRole",
    "require_role",
    "require_permission",
    "require_any_role",
    "RBACManager",
]

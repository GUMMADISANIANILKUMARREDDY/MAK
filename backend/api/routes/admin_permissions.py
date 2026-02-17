"""Admin: role permissions."""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from pydantic import BaseModel
from services.permission_service import get_role_permissions, get_all_permissions, set_permission
from api.dependencies import require_role

router = APIRouter(prefix="/admin", tags=["Admin - Permissions"])


class SetPermissionRequest(BaseModel):
    role: str
    resource: str
    action: str
    grant: bool


@router.get("/permissions")
def list_all_permissions(_=Depends(require_role(["admin"]))):
    """List all role-permission mappings."""
    return get_all_permissions()


@router.get("/permissions/role/{role}")
def list_role_permissions(role: str, _=Depends(require_role(["admin"]))):
    """List permissions for a role."""
    return get_role_permissions(role)


@router.post("/permissions")
def set_permission_route(data: SetPermissionRequest, _=Depends(require_role(["admin"]))):
    """Grant or revoke a permission."""
    result = set_permission(data.role, data.resource, data.action, data.grant)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import Optional
from services.activity_service import log_activity
from schemas.admin import (
    AdminCreateUserRequest,
    AdminBulkCreateUsersRequest,
    AdminUpdateUserRequest,
    AdminBulkDeleteRequest,
)
from services.user_management_service import (
    get_all_users,
    get_user_by_id,
    create_user,
    create_users_bulk,
    update_user,
    delete_user,
    delete_users_bulk,
)
from api.dependencies import require_role

router = APIRouter(prefix="/admin/users", tags=["Admin - Users"])


@router.get("/")
def list_users(
    role: Optional[str] = Query(None, description="Filter by role"),
    name: Optional[str] = Query(None, description="Search by username"),
    email: Optional[str] = Query(None, description="Search by email"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search username, email, userid"),
    sort: str = Query("userid", description="Sort field"),
    order: str = Query("asc", description="asc or desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    _=Depends(require_role(["admin"])),
):
    """Admin: List all users with filters, sort and pagination."""
    return get_all_users(role=role, name=name, email=email, active=active, search=search, sort=sort, order=order, page=page, limit=limit)


@router.get("/role/{role}")
def list_users_by_role(
    role: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    _=Depends(require_role(["admin"])),
):
    """Admin: Get users by specific role."""
    return get_all_users(role=role, page=page, limit=limit)


@router.get("/{userid}")
def get_user(userid: str, _=Depends(require_role(["admin"]))):
    """Admin: Get single user by userid."""
    result = get_user_by_id(userid)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result


@router.post("/single")
def create_single_user(data: AdminCreateUserRequest, request: Request, user: dict = Depends(require_role(["admin"]))):
    """Admin: Create single user (any role)."""
    result = create_user(
        userid=data.userid,
        username=data.username,
        email=data.email,
        password=data.password,
        role=data.role,
        active=data.active,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    log_activity(user["sub"], "create", "user", data.userid, {"role": data.role}, request.client.host if request.client else None)
    return result


@router.post("/bulk")
def create_bulk_users(data: AdminBulkCreateUsersRequest, _=Depends(require_role(["admin"]))):
    """Admin: Create multiple users."""
    users_dict = [user.model_dump() for user in data.users]
    return create_users_bulk(users_dict)


@router.put("/{userid}")
def update_user_endpoint(userid: str, data: AdminUpdateUserRequest, request: Request, user: dict = Depends(require_role(["admin"]))):
    """Admin: Update user."""
    updates = data.model_dump(exclude_unset=True)
    result = update_user(userid, updates)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    log_activity(user["sub"], "update", "user", userid, updates, request.client.host if request.client else None)
    return result


@router.delete("/{userid}")
def delete_user_endpoint(
    userid: str,
    request: Request,
    user: dict = Depends(require_role(["admin"])),
    soft: bool = Query(True, description="Soft delete (deactivate) or hard delete"),
):
    """Admin: Delete user (soft or hard)."""
    result = delete_user(userid, soft)
    if request and getattr(request, "client", None):
        log_activity(user["sub"], "delete", "user", userid, {"soft": soft}, request.client.host)
    return result


@router.post("/bulk-delete")
def bulk_delete_users(data: AdminBulkDeleteRequest, soft: bool = Query(True), _=Depends(require_role(["admin"]))):
    """Admin: Delete multiple users."""
    return delete_users_bulk(data.userids, soft)

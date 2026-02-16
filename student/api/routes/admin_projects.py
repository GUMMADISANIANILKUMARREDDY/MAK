from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from schemas.project import ProjectCreateRequest, ProjectUpdateRequest, ProjectAssignManagerRequest
from services.project_service import (
    create_project,
    get_all_projects,
    get_project_by_id,
    update_project,
    delete_project,
    assign_project_to_manager,
    get_project_managers,
)
from api.dependencies import require_role, get_current_user

router = APIRouter(prefix="/admin/projects", tags=["Admin - Projects"])


@router.get("/")
def list_projects(
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    _=Depends(require_role(["admin"])),
):
    """Admin: List all projects."""
    return get_all_projects(status=status, page=page, limit=limit)


@router.get("/{projectid}")
def get_project(projectid: str, _=Depends(require_role(["admin", "manager"]))):
    """Admin/Manager: Get project details."""
    result = get_project_by_id(projectid)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result


@router.post("/create")
def create_new_project(data: ProjectCreateRequest, current_user: dict = Depends(require_role(["admin"]))):
    """Admin: Create project."""
    result = create_project(
        title=data.title,
        description=data.description,
        created_by=current_user["sub"],
        start_date=data.start_date,
        end_date=data.end_date,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.put("/{projectid}")
def update_project_endpoint(projectid: str, data: ProjectUpdateRequest, _=Depends(require_role(["admin"]))):
    """Admin: Update project."""
    updates = data.model_dump(exclude_unset=True)
    result = update_project(projectid, updates)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.delete("/{projectid}")
def delete_project_endpoint(projectid: str, _=Depends(require_role(["admin"]))):
    """Admin: Delete project (cascades: modules, tasks, assignments)."""
    result = delete_project(projectid)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result


@router.post("/{projectid}/assign-manager")
def assign_manager(projectid: str, data: ProjectAssignManagerRequest, current_user: dict = Depends(require_role(["admin"]))):
    """Admin: Assign project to manager."""
    result = assign_project_to_manager(projectid, data.manager_userid, current_user["sub"])
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.get("/{projectid}/managers")
def list_project_managers(projectid: str, _=Depends(require_role(["admin", "manager"]))):
    """Admin/Manager: Get managers assigned to project."""
    return get_project_managers(projectid)

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from schemas.project import ModuleCreateRequest, ModuleUpdateRequest, ModuleAssignMentorRequest
from services.module_service import (
    create_module,
    get_project_modules,
    get_module_by_id,
    update_module,
    delete_module,
    assign_module_to_mentor,
    get_module_mentors,
)
from services.project_service import get_manager_projects
from api.dependencies import require_role, get_current_user

router = APIRouter(prefix="/manager", tags=["Manager - Modules"])


@router.get("/my-projects")
def my_projects(current_user: dict = Depends(require_role(["manager"]))):
    """Manager: Get projects assigned to me."""
    return get_manager_projects(current_user["sub"])


@router.get("/projects/{projectid}/modules")
def list_modules(
    projectid: str,
    search: Optional[str] = Query(None, description="Search title or description"),
    status: Optional[str] = Query(None, description="Filter by status"),
    sort: str = Query("created_at", description="Sort field"),
    order: str = Query("desc", description="asc or desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    _=Depends(require_role(["admin", "manager", "mentor"])),
):
    """Manager/Mentor: List modules in project with filters and sort."""
    return get_project_modules(projectid, search=search, status=status, sort=sort, order=order, page=page, limit=limit)


@router.get("/modules/{moduleid}")
def get_module(moduleid: str, _=Depends(require_role(["admin", "manager", "mentor"]))):
    """Manager/Mentor: Get module details."""
    result = get_module_by_id(moduleid)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result


@router.post("/projects/{projectid}/modules/create")
def create_new_module(projectid: str, data: ModuleCreateRequest, current_user: dict = Depends(require_role(["manager"]))):
    """Manager: Create module in project."""
    result = create_module(
        projectid=projectid,
        title=data.title,
        description=data.description,
        created_by=current_user["sub"],
        priority=data.priority,
        due_date=data.due_date,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.put("/modules/{moduleid}")
def update_module_endpoint(moduleid: str, data: ModuleUpdateRequest, _=Depends(require_role(["manager"]))):
    """Manager: Update module."""
    updates = data.model_dump(exclude_unset=True)
    result = update_module(moduleid, updates)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.delete("/modules/{moduleid}")
def delete_module_endpoint(moduleid: str, _=Depends(require_role(["manager"]))):
    """Manager: Delete module (cascades: tasks and task assignments)."""
    result = delete_module(moduleid)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result


@router.post("/modules/{moduleid}/assign-mentor")
def assign_mentor(moduleid: str, data: ModuleAssignMentorRequest, current_user: dict = Depends(require_role(["manager"]))):
    """Manager: Assign module to mentor."""
    result = assign_module_to_mentor(moduleid, data.mentor_userid, current_user["sub"])
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.get("/modules/{moduleid}/mentors")
def list_module_mentors(moduleid: str, _=Depends(require_role(["admin", "manager", "mentor"]))):
    """Manager/Mentor: Get mentors assigned to module."""
    return get_module_mentors(moduleid)

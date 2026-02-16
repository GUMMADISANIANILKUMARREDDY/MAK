from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from schemas.project import TaskStatusUpdateRequest, TaskSubmissionRequest
from services.task_service import get_student_tasks, update_task_assignment_status, submit_task, get_task_by_id
from api.dependencies import require_role, get_current_user

router = APIRouter(prefix="/student", tags=["Student - Tasks"])


@router.get("/my-tasks")
def my_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: dict = Depends(require_role(["student"])),
):
    """Student: Get all tasks assigned to me."""
    return get_student_tasks(current_user["sub"], status)


@router.get("/tasks/{taskid}")
def get_task_details(taskid: str, current_user: dict = Depends(require_role(["student"]))):
    """Student: Get task details."""
    result = get_task_by_id(taskid)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result


@router.put("/tasks/{assignment_id}/update-status")
def update_status(assignment_id: str, data: TaskStatusUpdateRequest, _=Depends(require_role(["student"]))):
    """Student: Update task status (assigned → in_progress → review)."""
    result = update_task_assignment_status(assignment_id, data.status)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.post("/tasks/{assignment_id}/submit")
def submit_task_endpoint(assignment_id: str, data: TaskSubmissionRequest, _=Depends(require_role(["student"]))):
    """Student: Submit task with notes."""
    result = submit_task(assignment_id, data.notes)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result

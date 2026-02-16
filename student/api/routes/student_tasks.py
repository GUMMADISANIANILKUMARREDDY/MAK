from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from schemas.project import TaskStatusUpdateRequest, TaskSubmissionRequest
from services.task_service import (
    get_student_tasks,
    update_task_assignment_status,
    submit_task,
    get_task_by_id,
    upload_submission_file,
)
from api.dependencies import require_role, get_current_user

router = APIRouter(prefix="/student", tags=["Student - Tasks"])


@router.get("/my-tasks")
def my_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search task title or description"),
    sort: str = Query("assigned_at", description="Sort field"),
    order: str = Query("desc", description="asc or desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(require_role(["student"])),
):
    """Student: Get all tasks assigned to me with filters and sort."""
    return get_student_tasks(current_user["sub"], status=status, search=search, sort=sort, order=order, page=page, limit=limit)


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
def submit_task_endpoint(
    assignment_id: str,
    notes: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    _=Depends(require_role(["student"])),
):
    """Student: Submit task with optional notes and/or file attachment."""
    submission_url = None
    if file and file.filename:
        content = file.file.read()
        content_type = file.content_type
        submission_url = upload_submission_file(assignment_id, file.filename, content, content_type)
        if not submission_url:
            raise HTTPException(status_code=500, detail="Failed to upload file. Try again.")
    result = submit_task(assignment_id, notes, submission_url)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result

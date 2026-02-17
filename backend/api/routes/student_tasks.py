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
from services.comment_service import (
    list_comments,
    create_comment,
    delete_comment,
    assignment_accessible_by_student,
)
from schemas.project import TaskCommentRequest
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
    """Student: Submit task with optional notes and/or file attachment. Resubmission allowed when rejected."""
    from services.task_service import validate_upload_file
    submission_url = None
    submission_path = None
    if file and file.filename:
        content = file.file.read()
        ok, err = validate_upload_file(len(content), file.filename)
        if not ok:
            raise HTTPException(status_code=400, detail=err)
        content_type = file.content_type
        out = upload_submission_file(assignment_id, file.filename, content, content_type)
        if not out:
            raise HTTPException(status_code=500, detail="Failed to upload file. Try again.")
        submission_url, submission_path = out
    result = submit_task(assignment_id, notes, submission_url, submission_path)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


# === TASK COMMENTS ===

@router.get("/tasks/assignments/{assignment_id}/comments")
def get_assignment_comments(assignment_id: str, current_user: dict = Depends(require_role(["student"]))):
    """Student: List comments for own assignment."""
    if not assignment_accessible_by_student(assignment_id, current_user["sub"]):
        raise HTTPException(status_code=404, detail="Assignment not found")
    return list_comments(assignment_id)


@router.post("/tasks/assignments/{assignment_id}/comments")
def add_assignment_comment(
    assignment_id: str,
    data: TaskCommentRequest,
    current_user: dict = Depends(require_role(["student"])),
):
    """Student: Add comment to own assignment."""
    if not assignment_accessible_by_student(assignment_id, current_user["sub"]):
        raise HTTPException(status_code=404, detail="Assignment not found")
    result = create_comment(assignment_id, current_user["sub"], data.comment)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.delete("/tasks/comments/{comment_id}")
def delete_comment_route(comment_id: str, current_user: dict = Depends(require_role(["student"]))):
    """Student: Delete own comment."""
    result = delete_comment(comment_id, current_user["sub"])
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from typing import Optional
from schemas.project import (
    TaskCreateRequest,
    TaskUpdateRequest,
    TaskAssignStudentRequest,
    TaskBulkAssignRequest,
    TaskReviewRequest,
    TaskCommentRequest,
    TeamCreateRequest,
    TeamAddStudentRequest,
)
from services.task_service import (
    create_task,
    get_module_tasks,
    get_task_by_id,
    update_task,
    delete_task,
    assign_task_to_student,
    assign_task_bulk,
    get_task_assignments,
    review_task,
    get_submission_download_url,
    upload_review_file,
)
from services.team_service import (
    create_team,
    get_mentor_teams,
    add_student_to_team,
    get_team_members,
    remove_student_from_team,
    delete_team,
)
from services.module_service import get_mentor_modules
from services.comment_service import (
    list_comments,
    create_comment,
    delete_comment,
    assignment_accessible_by_mentor,
)
from api.dependencies import require_role, get_current_user

router = APIRouter(prefix="/mentor", tags=["Mentor - Tasks & Teams"])


# === MY MODULES ===

@router.get("/my-modules")
def my_modules(current_user: dict = Depends(require_role(["mentor"]))):
    """Mentor: Get modules assigned to me."""
    return get_mentor_modules(current_user["sub"])


# === TEAMS ===

@router.post("/teams/create")
def create_new_team(data: TeamCreateRequest, current_user: dict = Depends(require_role(["mentor"]))):
    """Mentor: Create student team."""
    result = create_team(data.team_name, current_user["sub"])
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.get("/teams")
def list_teams(current_user: dict = Depends(require_role(["mentor"]))):
    """Mentor: Get my teams."""
    return get_mentor_teams(current_user["sub"])


@router.post("/teams/{teamid}/add-student")
def add_student(teamid: str, data: TeamAddStudentRequest, _=Depends(require_role(["mentor"]))):
    """Mentor: Add student to team."""
    result = add_student_to_team(teamid, data.student_userid)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.get("/teams/{teamid}/members")
def list_team_members(teamid: str, _=Depends(require_role(["mentor"]))):
    """Mentor: Get students in team."""
    return get_team_members(teamid)


@router.delete("/teams/{teamid}/remove-student/{student_userid}")
def remove_student(teamid: str, student_userid: str, _=Depends(require_role(["mentor"]))):
    """Mentor: Remove student from team."""
    return remove_student_from_team(teamid, student_userid)


@router.delete("/teams/{teamid}")
def delete_team_endpoint(teamid: str, _=Depends(require_role(["mentor"]))):
    """Mentor: Delete team."""
    return delete_team(teamid)


# === TASKS ===

@router.get("/modules/{moduleid}/tasks")
def list_tasks(
    moduleid: str,
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search title or description"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    date_from: Optional[str] = Query(None, description="Due date from (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Due date to (YYYY-MM-DD)"),
    sort: str = Query("created_at", description="Sort field"),
    order: str = Query("desc", description="asc or desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    _=Depends(require_role(["mentor"])),
):
    """Mentor: List tasks in module with filters and sort."""
    from datetime import date as date_type
    d_from = date_type.fromisoformat(date_from) if date_from else None
    d_to = date_type.fromisoformat(date_to) if date_to else None
    return get_module_tasks(moduleid, status=status, search=search, priority=priority, date_from=d_from, date_to=d_to, sort=sort, order=order, page=page, limit=limit)


@router.get("/tasks/{taskid}")
def get_task(taskid: str, _=Depends(require_role(["mentor", "student"]))):
    """Mentor/Student: Get task details."""
    result = get_task_by_id(taskid)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result


@router.post("/modules/{moduleid}/tasks/create")
def create_new_task(moduleid: str, data: TaskCreateRequest, current_user: dict = Depends(require_role(["mentor"]))):
    """Mentor: Create task in module."""
    result = create_task(
        moduleid=moduleid,
        title=data.title,
        description=data.description,
        task_type=data.task_type,
        created_by=current_user["sub"],
        priority=data.priority,
        story_points=data.story_points,
        due_date=data.due_date,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.put("/tasks/{taskid}")
def update_task_endpoint(taskid: str, data: TaskUpdateRequest, _=Depends(require_role(["mentor"]))):
    """Mentor: Update task."""
    updates = data.model_dump(exclude_unset=True)
    result = update_task(taskid, updates)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.delete("/tasks/{taskid}")
def delete_task_endpoint(taskid: str, _=Depends(require_role(["mentor"]))):
    """Mentor: Delete task."""
    return delete_task(taskid)


@router.post("/tasks/{taskid}/assign-student")
def assign_student(taskid: str, data: TaskAssignStudentRequest, current_user: dict = Depends(require_role(["mentor"]))):
    """Mentor: Assign task to single student."""
    result = assign_task_to_student(taskid, data.student_userid, current_user["sub"])
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.post("/tasks/{taskid}/bulk-assign")
def bulk_assign_students(taskid: str, data: TaskBulkAssignRequest, current_user: dict = Depends(require_role(["mentor"]))):
    """Mentor: Assign task to multiple students."""
    return assign_task_bulk(taskid, data.student_userids, current_user["sub"])


@router.get("/tasks/{taskid}/assignments")
def list_task_assignments(taskid: str, _=Depends(require_role(["mentor"]))):
    """Mentor: Get all assignments for task."""
    return get_task_assignments(taskid)


@router.get("/tasks/assignments/{assignment_id}/submission")
def get_submission_url(assignment_id: str, current_user: dict = Depends(require_role(["mentor"]))):
    """Mentor: Get signed URL to download student submission file."""
    if not assignment_accessible_by_mentor(assignment_id, current_user["sub"]):
        raise HTTPException(status_code=404, detail="Assignment not found")
    out = get_submission_download_url(assignment_id)
    if not out:
        raise HTTPException(status_code=404, detail="No submission file")
    return out


@router.post("/tasks/assignments/{assignment_id}/review-file")
def upload_review_file_route(
    assignment_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(require_role(["mentor"])),
):
    """Mentor: Upload review file for assignment."""
    if not assignment_accessible_by_mentor(assignment_id, current_user["sub"]):
        raise HTTPException(status_code=404, detail="Assignment not found")
    content = file.file.read()
    url = upload_review_file(assignment_id, file.filename or "file", content, file.content_type)
    if not url:
        raise HTTPException(status_code=400, detail="Upload failed or file type/size not allowed")
    return {"success": True, "review_file_url": url}


@router.post("/tasks/assignments/{assignment_id}/review")
def review_assignment(
    assignment_id: str,
    data: TaskReviewRequest,
    current_user: dict = Depends(require_role(["mentor"])),
):
    """Mentor: Approve or reject task submission with feedback and optional score."""
    result = review_task(
        assignment_id,
        current_user["sub"],
        data.result,
        data.feedback,
        data.score,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


# === TASK COMMENTS ===

@router.get("/tasks/assignments/{assignment_id}/comments")
def get_assignment_comments(assignment_id: str, current_user: dict = Depends(require_role(["mentor"]))):
    """Mentor: List comments for an assignment (must be in your module)."""
    if not assignment_accessible_by_mentor(assignment_id, current_user["sub"]):
        raise HTTPException(status_code=404, detail="Assignment not found")
    return list_comments(assignment_id)


@router.post("/tasks/assignments/{assignment_id}/comments")
def add_assignment_comment(
    assignment_id: str,
    data: TaskCommentRequest,
    current_user: dict = Depends(require_role(["mentor"])),
):
    """Mentor: Add comment to assignment."""
    if not assignment_accessible_by_mentor(assignment_id, current_user["sub"]):
        raise HTTPException(status_code=404, detail="Assignment not found")
    result = create_comment(assignment_id, current_user["sub"], data.comment)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.delete("/tasks/comments/{comment_id}")
def delete_comment_route(comment_id: str, current_user: dict = Depends(require_role(["mentor"]))):
    """Mentor: Delete own comment."""
    result = delete_comment(comment_id, current_user["sub"])
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result

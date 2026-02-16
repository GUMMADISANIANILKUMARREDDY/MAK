from fastapi import APIRouter, Depends, HTTPException
from services.dashboard_service import (
    get_admin_stats,
    get_manager_stats,
    get_mentor_stats,
    get_student_stats,
)
from api.dependencies import require_role, get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/admin-stats")
def admin_stats(current_user: dict = Depends(require_role(["admin"]))):
    """Admin: total users, students, projects; active vs inactive."""
    return get_admin_stats()


@router.get("/manager-stats")
def manager_stats(current_user: dict = Depends(require_role(["manager"]))):
    """Manager: modules by status, tasks pending review."""
    return get_manager_stats(current_user["sub"])


@router.get("/mentor-stats")
def mentor_stats(current_user: dict = Depends(require_role(["mentor"]))):
    """Mentor: tasks pending review, teams count."""
    return get_mentor_stats(current_user["sub"])


@router.get("/student-stats")
def student_stats(current_user: dict = Depends(require_role(["student"]))):
    """Student: task counts by status."""
    return get_student_stats(current_user["sub"])

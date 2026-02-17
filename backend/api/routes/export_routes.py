"""CSV export endpoints."""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from services.export_service import stream_students_csv, stream_projects_csv, stream_mentor_tasks_csv
from api.dependencies import require_role

router = APIRouter(tags=["Export"])


def _stream_csv(generator, filename: str):
    return StreamingResponse(
        generator,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/admin/export/students")
def export_students(_=Depends(require_role(["admin"]))):
    """Admin: Export students as CSV."""
    return _stream_csv(stream_students_csv(), "students.csv")


@router.get("/admin/export/projects")
def export_projects(_=Depends(require_role(["admin"]))):
    """Admin: Export projects as CSV."""
    return _stream_csv(stream_projects_csv(), "projects.csv")


@router.get("/mentor/export/tasks")
def export_mentor_tasks(current_user: dict = Depends(require_role(["mentor"]))):
    """Mentor: Export my tasks and assignments as CSV."""
    return _stream_csv(stream_mentor_tasks_csv(current_user["sub"]), "mentor-tasks.csv")

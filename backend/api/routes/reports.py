"""Admin reports: PDF and Excel download."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from services.report_service import project_summary_excel, project_summary_pdf, student_progress_excel
from api.dependencies import require_role

router = APIRouter(prefix="/admin/reports", tags=["Reports"])


@router.get("/project-summary.xlsx")
def report_project_summary_excel(_=Depends(require_role(["admin"]))):
    """Download project summary as Excel."""
    buf = project_summary_excel()
    if not buf:
        raise HTTPException(status_code=500, detail="Excel library not available")
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=project-summary.xlsx"},
    )


@router.get("/project-summary.pdf")
def report_project_summary_pdf(_=Depends(require_role(["admin"]))):
    """Download project summary as PDF."""
    buf = project_summary_pdf()
    if not buf:
        raise HTTPException(status_code=500, detail="PDF library not available")
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=project-summary.pdf"},
    )


@router.get("/student-progress.xlsx")
def report_student_progress_excel(_=Depends(require_role(["admin"]))):
    """Download student progress as Excel."""
    buf = student_progress_excel()
    if not buf:
        raise HTTPException(status_code=500, detail="Excel library not available")
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=student-progress.xlsx"},
    )

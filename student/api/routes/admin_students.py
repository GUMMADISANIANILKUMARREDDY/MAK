from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from schemas.admin import (
    AdminCreateStudentRequest,
    AdminBulkCreateStudentsRequest,
    AdminUpdateStudentRequest,
    AdminBulkDeleteRequest,
)
from services.student_management_service import (
    get_all_students,
    get_student_by_id,
    create_student,
    create_students_bulk,
    update_student,
    delete_student,
    delete_students_bulk,
)
from api.dependencies import require_role

router = APIRouter(prefix="/admin/students", tags=["Admin - Students"])


@router.get("/")
def list_students(
    name: Optional[str] = Query(None, description="Search by first or last name"),
    email: Optional[str] = Query(None, description="Search by email"),
    userid: Optional[str] = Query(None, description="Search by userid"),
    search: Optional[str] = Query(None, description="Search name, email, userid"),
    sort: str = Query("userid", description="Sort field"),
    order: str = Query("asc", description="asc or desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    _=Depends(require_role(["admin"])),
):
    """Admin: List all students with filters, sort and pagination."""
    return get_all_students(name=name, email=email, userid=userid, search=search, sort=sort, order=order, page=page, limit=limit)


@router.get("/{userid}")
def get_student(userid: str, _=Depends(require_role(["admin"]))):
    """Admin: Get single student by userid."""
    result = get_student_by_id(userid)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result


@router.post("/single")
def create_single_student(data: AdminCreateStudentRequest, _=Depends(require_role(["admin"]))):
    """Admin: Create single student entry (user must exist in users table)."""
    result = create_student(
        userid=data.userid, first_name=data.first_name, last_name=data.last_name, phone=data.phone, email=data.email
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.post("/bulk")
def create_bulk_students(data: AdminBulkCreateStudentsRequest, _=Depends(require_role(["admin"]))):
    """Admin: Create multiple students."""
    students_dict = [student.model_dump() for student in data.students]
    return create_students_bulk(students_dict)


@router.put("/{userid}")
def update_student_endpoint(userid: str, data: AdminUpdateStudentRequest, _=Depends(require_role(["admin"]))):
    """Admin: Update student."""
    updates = data.model_dump(exclude_unset=True)
    result = update_student(userid, updates)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.delete("/{userid}")
def delete_student_endpoint(userid: str, _=Depends(require_role(["admin"]))):
    """Admin: Delete student from students table."""
    return delete_student(userid)


@router.post("/bulk-delete")
def bulk_delete_students(data: AdminBulkDeleteRequest, _=Depends(require_role(["admin"]))):
    """Admin: Delete multiple students."""
    return delete_students_bulk(data.userids)

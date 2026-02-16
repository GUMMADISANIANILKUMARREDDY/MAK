from typing import Optional
from config.supabase_client import supabase


def get_all_students(
    name: Optional[str] = None,
    email: Optional[str] = None,
    userid: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> dict:
    """Admin: fetch students with filters and pagination."""
    query = supabase.table("students").select("*")

    if name:
        query = query.or_(f"first_name.ilike.%{name}%,last_name.ilike.%{name}%")
    if email:
        query = query.ilike("email", f"%{email}%")
    if userid:
        query = query.ilike("userid", f"%{userid}%")

    offset = (page - 1) * limit
    result = query.range(offset, offset + limit - 1).execute()

    return {"success": True, "students": result.data or [], "page": page, "limit": limit}


def get_student_by_id(userid: str) -> dict:
    """Admin: get single student by userid."""
    result = supabase.table("students").select("*").eq("userid", userid).execute()
    if not result.data or len(result.data) == 0:
        return {"success": False, "message": "Student not found"}
    return {"success": True, "student": result.data[0]}


def create_student(userid: str, first_name: str, last_name: str, phone: str, email: str) -> dict:
    """Admin: create single student entry (assumes user exists in users table)."""
    # Check if userid exists in users
    user_check = supabase.table("users").select("userid").eq("userid", userid).execute()
    if not user_check.data or len(user_check.data) == 0:
        return {"success": False, "message": f"User {userid} not found in users table. Create user first."}

    # Check if student already exists
    existing = supabase.table("students").select("userid").eq("userid", userid).execute()
    if existing.data and len(existing.data) > 0:
        return {"success": False, "message": "Student already exists"}

    result = supabase.table("students").insert(
        {"userid": userid, "first_name": first_name, "last_name": last_name, "phone": phone, "email": email}
    ).execute()

    if not result.data:
        return {"success": False, "message": "Failed to create student"}

    return {"success": True, "message": "Student created", "student": result.data[0]}


def create_students_bulk(students: list) -> dict:
    """Admin: create multiple students."""
    created = []
    errors = []

    for student in students:
        result = create_student(
            userid=student["userid"],
            first_name=student["first_name"],
            last_name=student["last_name"],
            phone=student["phone"],
            email=student["email"],
        )
        if result.get("success"):
            created.append(result.get("student"))
        else:
            errors.append({"userid": student["userid"], "error": result.get("message")})

    return {"success": True, "created": len(created), "errors": errors, "students": created}


def update_student(userid: str, updates: dict) -> dict:
    """Admin: update student fields."""
    if not updates:
        return {"success": False, "message": "No updates provided"}

    updates = {k: v for k, v in updates.items() if v is not None}

    result = supabase.table("students").update(updates).eq("userid", userid).execute()
    if not result.data or len(result.data) == 0:
        return {"success": False, "message": "Student not found or update failed"}

    return {"success": True, "message": "Student updated", "student": result.data[0]}


def delete_student(userid: str) -> dict:
    """Admin: delete student from students table (users table entry remains)."""
    result = supabase.table("students").delete().eq("userid", userid).execute()
    return {"success": True, "message": f"Student {userid} deleted from students table"}


def delete_students_bulk(userids: list) -> dict:
    """Admin: delete multiple students."""
    deleted = []

    for userid in userids:
        result = delete_student(userid)
        if result.get("success"):
            deleted.append(userid)

    return {"success": True, "deleted": len(deleted)}

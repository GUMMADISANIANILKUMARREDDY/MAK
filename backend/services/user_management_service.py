from typing import Optional
from config.supabase_client import supabase
from services.auth_service import hash_password


VALID_ROLES = ["student", "mentor", "clgadmin", "admin", "manager"]


def get_all_users(
    role: Optional[str] = None,
    name: Optional[str] = None,
    email: Optional[str] = None,
    active: Optional[bool] = None,
    search: Optional[str] = None,
    sort: str = "userid",
    order: str = "asc",
    page: int = 1,
    limit: int = 20,
) -> dict:
    """Admin: fetch users with filters, sort and pagination."""
    query = supabase.table("users").select("*", count="exact")
    if role:
        query = query.eq("role", role)
    if name:
        query = query.or_(f"username.ilike.%{name}%")
    if email:
        query = query.ilike("email", f"%{email}%")
    if search and search.strip():
        q = search.strip()
        query = query.or_(f"username.ilike.%{q}%,email.ilike.%{q}%,userid.ilike.%{q}%")
    if active is not None:
        query = query.eq("active", active)
    sort_col = sort if sort in ("userid", "username", "email", "role", "active") else "userid"
    desc = order.lower() == "desc"
    offset = (page - 1) * limit
    result = query.range(offset, offset + limit - 1).order(sort_col, desc=desc).execute()
    total = getattr(result, "count", None)
    if total is None and result.data is not None:
        total = len(result.data)
    return {"success": True, "users": result.data or [], "page": page, "limit": limit, "total": total}


def get_user_by_id(userid: str) -> dict:
    """Admin: get single user by userid."""
    result = supabase.table("users").select("*").eq("userid", userid).execute()
    if not result.data or len(result.data) == 0:
        return {"success": False, "message": "User not found"}
    return {"success": True, "user": result.data[0]}


def create_user(userid: str, username: str, email: str, password: str, role: str, active: bool = True) -> dict:
    """Admin: create single user (any role)."""
    if role not in VALID_ROLES:
        return {"success": False, "message": f"Invalid role. Must be one of: {', '.join(VALID_ROLES)}"}

    existing = supabase.table("users").select("userid").eq("userid", userid).execute()
    if existing.data and len(existing.data) > 0:
        return {"success": False, "message": "User ID already exists"}

    existing_email = supabase.table("users").select("email").eq("email", email).execute()
    if existing_email.data and len(existing_email.data) > 0:
        return {"success": False, "message": "Email already exists"}

    hashed = hash_password(password)
    result = supabase.table("users").insert(
        {"userid": userid, "username": username, "email": email, "password": hashed, "role": role, "active": active}
    ).execute()

    if not result.data:
        return {"success": False, "message": "Failed to create user"}

    return {"success": True, "message": "User created", "user": result.data[0]}


def create_users_bulk(users: list) -> dict:
    """Admin: create multiple users."""
    created = []
    errors = []

    for user in users:
        result = create_user(
            userid=user["userid"],
            username=user["username"],
            email=user["email"],
            password=user["password"],
            role=user["role"],
            active=user.get("active", True),
        )
        if result.get("success"):
            created.append(result.get("user"))
        else:
            errors.append({"userid": user["userid"], "error": result.get("message")})

    return {"success": True, "created": len(created), "errors": errors, "users": created}


def update_user(userid: str, updates: dict) -> dict:
    """Admin: update user fields."""
    if not updates:
        return {"success": False, "message": "No updates provided"}

    if "password" in updates and updates["password"]:
        updates["password"] = hash_password(updates["password"])

    if "role" in updates and updates["role"] not in VALID_ROLES:
        return {"success": False, "message": f"Invalid role. Must be one of: {', '.join(VALID_ROLES)}"}

    updates = {k: v for k, v in updates.items() if v is not None}

    result = supabase.table("users").update(updates).eq("userid", userid).execute()
    if not result.data or len(result.data) == 0:
        return {"success": False, "message": "User not found or update failed"}

    return {"success": True, "message": "User updated", "user": result.data[0]}


def delete_user(userid: str, soft: bool = True) -> dict:
    """Admin: delete user (soft or hard delete)."""
    if soft:
        result = supabase.table("users").update({"active": False}).eq("userid", userid).execute()
        if not result.data or len(result.data) == 0:
            return {"success": False, "message": "User not found"}
        return {"success": True, "message": f"User {userid} deactivated"}
    else:
        result = supabase.table("users").delete().eq("userid", userid).execute()
        return {"success": True, "message": f"User {userid} deleted permanently"}


def delete_users_bulk(userids: list, soft: bool = True) -> dict:
    """Admin: delete multiple users."""
    deleted = []
    errors = []

    for userid in userids:
        result = delete_user(userid, soft)
        if result.get("success"):
            deleted.append(userid)
        else:
            errors.append({"userid": userid, "error": result.get("message")})

    return {"success": True, "deleted": len(deleted), "errors": errors}

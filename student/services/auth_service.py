import random
import string
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from config.settings import settings
from config.supabase_client import supabase
from schemas.user import UserResponse
from services.email_service import send_otp_email


def hash_password(password: str) -> str:
    """Hash password with bcrypt. Bcrypt limit 72 bytes - truncate if longer."""
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode("utf-8")[:72]
    return bcrypt.checkpw(pwd_bytes, hashed_password.encode("utf-8"))


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def login_user(userid: Optional[str], email: Optional[str], password: str) -> Optional[dict]:
    """Fetch user from Supabase users table by userid or email and verify password."""
    if userid:
        response = supabase.table("users").select("userid, username, email, password, role, active").eq("userid", userid).execute()
    elif email:
        response = supabase.table("users").select("userid, username, email, password, role, active").eq("email", email).execute()
    else:
        return None

    if not response.data or len(response.data) == 0:
        return None

    user = response.data[0]

    if not user.get("active", True):
        return None

    if not verify_password(password, user["password"]):
        return None

    return {
        "userid": str(user["userid"]),
        "username": user["username"],
        "email": user["email"],
        "role": user.get("role", "student"),
        "active": user.get("active", True),
    }


def generate_otp() -> str:
    return "".join(random.choices(string.digits, k=6))


def register_student(
    userid: str,
    first_name: str,
    last_name: str,
    phone: str,
    email: str,
    password: str,
) -> dict:
    """Store in pending_registrations, send OTP. Complete registration after verify_email_otp."""
    # Check userid unique in users
    existing_userid = supabase.table("users").select("userid").eq("userid", userid).execute()
    if existing_userid.data and len(existing_userid.data) > 0:
        return {"success": False, "message": "User ID / Roll number already registered"}

    # Check email unique in users
    existing_email = supabase.table("users").select("email").eq("email", email).execute()
    if existing_email.data and len(existing_email.data) > 0:
        return {"success": False, "message": "Email already registered"}

    # Delete old pending for same email (allow re-register)
    supabase.table("pending_registrations").delete().eq("email", email).execute()

    # Hash password - store in pending (will move to users on verify)
    hashed = hash_password(password)
    otp = generate_otp()
    expires_at = (datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)).isoformat()

    # Insert into pending_registrations
    supabase.table("pending_registrations").insert(
        {
            "email": email,
            "userid": userid,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "password": hashed,
            "otp": otp,
            "expires_at": expires_at,
        }
    ).execute()

    # Send OTP email
    if not send_otp_email(email, otp):
        supabase.table("pending_registrations").delete().eq("email", email).execute()
        return {"success": False, "message": "Failed to send OTP email. Try again."}

    return {
        "success": True,
        "message": f"OTP sent to {email}. Verify within {settings.OTP_EXPIRE_MINUTES} minutes.",
        "email": email,
    }


def verify_email_otp(email: str, otp: str) -> dict:
    """Verify OTP, then insert into users + students. Delete pending row."""
    response = supabase.table("pending_registrations").select("*").eq("email", email).execute()
    if not response.data or len(response.data) == 0:
        return {"success": False, "message": "Invalid or expired OTP. Please register again."}

    pending = response.data[0]

    if pending["otp"] != otp:
        return {"success": False, "message": "Invalid OTP"}

    exp = pending["expires_at"]
    if isinstance(exp, str):
        exp = datetime.fromisoformat(exp.replace("Z", "+00:00"))
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > exp:
        supabase.table("pending_registrations").delete().eq("email", email).execute()
        return {"success": False, "message": "OTP expired. Please register again."}

    userid = pending["userid"]
    first_name = pending["first_name"]
    last_name = pending["last_name"]
    phone = pending["phone"]
    hashed = pending["password"]
    username = f"{first_name} {last_name}".strip()

    # Insert into users
    user_result = supabase.table("users").insert(
        {
            "userid": userid,
            "username": username,
            "email": email,
            "password": hashed,
            "role": "student",
            "active": True,
        }
    ).execute()

    if not user_result.data:
        return {"success": False, "message": "Verification failed. Try again."}

    # Insert into students
    student_result = supabase.table("students").insert(
        {
            "userid": userid,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "email": email,
        }
    ).execute()

    if not student_result.data:
        supabase.table("users").delete().eq("userid", userid).execute()
        return {"success": False, "message": "Verification failed. Try again."}

    # Delete pending
    supabase.table("pending_registrations").delete().eq("email", email).execute()

    user = user_result.data[0]
    return {
        "success": True,
        "message": "Email verified. Registration complete.",
        "user": {
            "userid": user["userid"],
            "username": user["username"],
            "email": user["email"],
            "role": "student",
        },
    }


def admin_add_user(
    userid: str,
    username: str,
    email: str,
    password: str,
    role: str,
    active: bool = True,
) -> dict:
    """Admin-only: manually add user for any role (student, mentor, clgadmin, admin, manager). No OTP."""
    # Check userid unique
    existing_userid = supabase.table("users").select("userid").eq("userid", userid).execute()
    if existing_userid.data and len(existing_userid.data) > 0:
        return {"success": False, "message": "User ID already exists"}

    # Check email unique
    existing_email = supabase.table("users").select("email").eq("email", email).execute()
    if existing_email.data and len(existing_email.data) > 0:
        return {"success": False, "message": "Email already registered"}

    # Hash password
    hashed = hash_password(password)

    # Insert into users
    user_result = supabase.table("users").insert(
        {
            "userid": userid,
            "username": username,
            "email": email,
            "password": hashed,
            "role": role,
            "active": active,
        }
    ).execute()

    if not user_result.data:
        return {"success": False, "message": "Failed to add user"}

    user = user_result.data[0]
    return {
        "success": True,
        "message": f"User {username} ({role}) added successfully",
        "user": {
            "userid": user["userid"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "active": user.get("active", True),
        },
    }

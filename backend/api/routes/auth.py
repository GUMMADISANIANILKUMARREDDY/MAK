from fastapi import APIRouter, Depends, HTTPException
from schemas.user import (
    LoginRequest,
    StudentRegisterRequest,
    VerifyEmailRequest,
    AdminAddUserRequest,
    LoginResponse,
    UserResponse,
    ResendOtpRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    RefreshTokenRequest,
)
from services.auth_service import (
    login_user,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    register_student,
    verify_email_otp,
    resend_otp,
    change_password,
    forgot_password,
    reset_password,
    admin_add_user,
)
from api.dependencies import get_current_user, require_role, rate_limit_auth

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register_student_api(data: StudentRegisterRequest, _=Depends(rate_limit_auth)):
    """Student registration step 1: validate, store pending, send OTP to email."""
    result = register_student(
        userid=data.userid,
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone,
        email=data.email,
        password=data.password,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Registration failed"))
    return result


@router.post("/verify-email")
def verify_email_api(data: VerifyEmailRequest):
    """Student registration step 2: verify OTP, then complete registration (users + students)."""
    result = verify_email_otp(data.email, data.otp)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Verification failed"))
    return result


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, _=Depends(rate_limit_auth)):
    """Login API - accept userid or email with password. Returns JWT and refresh token."""
    if not data.userid and not data.email:
        raise HTTPException(status_code=400, detail="Provide userid or email")
    user = login_user(data.userid, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid userid/email or password")

    # Phase 1: Deadline approaching — notify student for tasks due in next N days (once per login)
    if user.get("role") == "student":
        try:
            from services.deadline_service import check_deadlines_for_user
            check_deadlines_for_user(user["userid"])
        except Exception:
            pass

    access_token = create_access_token(
        data={
            "sub": user["userid"],
            "email": user["email"],
            "role": user["role"],
            "username": user["username"],
        }
    )
    refresh_token = create_refresh_token(user["userid"])

    return LoginResponse(
        success=True,
        message="Login successful",
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(
            userid=user["userid"],
            username=user["username"],
            email=user["email"],
            role=user["role"],
            active=user["active"],
        ),
    )


@router.post("/resend-otp")
def resend_otp_api(data: ResendOtpRequest, _=Depends(rate_limit_auth)):
    """Resend OTP for pending registration (same email)."""
    result = resend_otp(data.email)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.post("/change-password")
def change_password_api(data: ChangePasswordRequest, user: dict = Depends(get_current_user)):
    """Change password for logged-in user (current + new password)."""
    result = change_password(user["sub"], data.current_password, data.new_password)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.post("/forgot-password")
def forgot_password_api(data: ForgotPasswordRequest, _=Depends(rate_limit_auth)):
    """Request password reset: sends OTP to email."""
    result = forgot_password(data.email)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.post("/reset-password")
def reset_password_api(data: ResetPasswordRequest, _=Depends(rate_limit_auth)):
    """Reset password with email + OTP from forgot-password email."""
    result = reset_password(data.email, data.otp, data.new_password)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.post("/refresh", response_model=LoginResponse)
def refresh_api(data: RefreshTokenRequest):
    """Exchange refresh token for new access token (and new refresh token)."""
    user = verify_refresh_token(data.refresh_token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    access_token = create_access_token(
        data={
            "sub": user["userid"],
            "email": user["email"],
            "role": user["role"],
            "username": user["username"],
        }
    )
    new_refresh = create_refresh_token(user["userid"])
    return LoginResponse(
        success=True,
        message="Token refreshed",
        access_token=access_token,
        refresh_token=new_refresh,
        user=UserResponse(
            userid=user["userid"],
            username=user["username"],
            email=user["email"],
            role=user["role"],
            active=user["active"],
        ),
    )


@router.get("/me")
def get_me(user: dict = Depends(get_current_user)):
    """Get current user from JWT. Frontend uses this + role to show different views."""
    return {"userid": user["sub"], "email": user["email"], "role": user["role"], "username": user.get("username")}


@router.get("/admin-only")
def admin_only(user: dict = Depends(require_role(["admin"]))):
    """Example: only admins can access. Use require_role(["admin", "company"]) for multiple roles."""
    return {"message": f"Welcome admin {user.get('username')}"}


@router.post("/admin/add-user")
def admin_add_user_api(data: AdminAddUserRequest, current_user: dict = Depends(require_role(["admin"]))):
    """Admin-only: manually add user for any role (student, mentor, clgadmin, admin, manager)."""
    valid_roles = ["student", "mentor", "clgadmin", "admin", "manager"]
    if data.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}")

    result = admin_add_user(
        userid=data.userid,
        username=data.username,
        email=data.email,
        password=data.password,
        role=data.role,
        active=data.active,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Failed to add user"))
    return result

from pydantic import BaseModel, model_validator
from typing import Optional


class LoginRequest(BaseModel):
    userid: Optional[str] = None
    email: Optional[str] = None
    password: str


class StudentRegisterRequest(BaseModel):
    userid: str  # roll number / user id
    first_name: str
    last_name: str
    phone: str
    email: str
    password: str
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class VerifyEmailRequest(BaseModel):
    email: str
    otp: str


class AdminAddUserRequest(BaseModel):
    userid: str
    username: str
    email: str
    password: str
    role: str  # student, mentor, clgadmin, admin, manager
    active: bool = True


class UserResponse(BaseModel):
    userid: str
    username: str
    email: str
    role: str
    active: bool


class LoginResponse(BaseModel):
    success: bool
    message: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    user: Optional[UserResponse] = None


class ResendOtpRequest(BaseModel):
    email: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    email: str
    otp: str
    new_password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str

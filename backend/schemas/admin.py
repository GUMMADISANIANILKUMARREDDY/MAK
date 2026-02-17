from pydantic import BaseModel
from typing import Optional, List


# === USER MANAGEMENT (all roles) ===

class AdminCreateUserRequest(BaseModel):
    userid: str
    username: str
    email: str
    password: str
    role: str
    active: bool = True


class AdminBulkCreateUsersRequest(BaseModel):
    users: List[AdminCreateUserRequest]


class AdminUpdateUserRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    active: Optional[bool] = None


class AdminBulkDeleteRequest(BaseModel):
    userids: List[str]


# === STUDENT MANAGEMENT (students table) ===

class AdminCreateStudentRequest(BaseModel):
    userid: str
    first_name: str
    last_name: str
    phone: str
    email: str


class AdminBulkCreateStudentsRequest(BaseModel):
    students: List[AdminCreateStudentRequest]


class AdminUpdateStudentRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class StudentDetailResponse(BaseModel):
    studentid: str
    userid: str
    first_name: str
    last_name: str
    phone: str
    email: str
    created_at: str
    updated_at: str

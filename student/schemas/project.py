from pydantic import BaseModel
from typing import Optional, List
from datetime import date


# === PROJECTS ===

class ProjectCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ProjectUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ProjectAssignManagerRequest(BaseModel):
    manager_userid: str


# === MODULES ===

class ModuleCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    due_date: Optional[date] = None


class ModuleUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None


class ModuleAssignMentorRequest(BaseModel):
    mentor_userid: str


# === TEAMS ===

class TeamCreateRequest(BaseModel):
    team_name: str


class TeamAddStudentRequest(BaseModel):
    student_userid: str


# === TASKS ===

class TaskCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    task_type: str = "task"
    priority: str = "medium"
    story_points: int = 0
    due_date: Optional[date] = None


class TaskUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    task_type: Optional[str] = None
    priority: Optional[str] = None
    story_points: Optional[int] = None
    status: Optional[str] = None
    due_date: Optional[date] = None


class TaskAssignStudentRequest(BaseModel):
    student_userid: str


class TaskBulkAssignRequest(BaseModel):
    student_userids: List[str]


class TaskStatusUpdateRequest(BaseModel):
    status: str


class TaskSubmissionRequest(BaseModel):
    notes: Optional[str] = None

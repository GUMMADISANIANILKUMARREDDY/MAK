"""Admin: colleges (multi-tenant)."""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from services.college_service import get_all_colleges, create_college
from api.dependencies import require_role

router = APIRouter(prefix="/admin", tags=["Admin - Colleges"])


class CollegeCreateRequest(BaseModel):
    name: str
    code: Optional[str] = None


@router.get("/colleges")
def list_colleges(_=Depends(require_role(["admin"]))):
    """List all colleges."""
    return get_all_colleges()


@router.post("/colleges")
def create_college_route(data: CollegeCreateRequest, _=Depends(require_role(["admin"]))):
    """Create college."""
    result = create_college(data.name, data.code)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result

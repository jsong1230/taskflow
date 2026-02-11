from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.project import ProjectRole


class ProjectCreate(BaseModel):
    name: str
    description: str = ""


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    owner_id: int
    created_at: datetime


class ProjectMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    project_id: int
    role: ProjectRole


class ProjectDetailResponse(ProjectResponse):
    members: list[ProjectMemberResponse] = []


class ProjectMemberAdd(BaseModel):
    user_id: int
    role: ProjectRole = ProjectRole.member

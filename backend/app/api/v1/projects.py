from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, get_project_member
from app.models.project import ProjectMember, ProjectRole
from app.models.task import TaskPriority, TaskStatus
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.project import (
    ProjectCreate,
    ProjectDetailResponse,
    ProjectMemberAdd,
    ProjectMemberResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.schemas.task import (
    TaskCreate,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.services.comment import create_comment, get_task_comments
from app.services.project import (
    add_project_member,
    create_project,
    delete_project,
    get_project_by_id,
    get_user_projects,
    update_project,
)
from app.services.task import (
    create_task,
    delete_task,
    get_task_by_id,
    get_tasks,
    update_task,
    update_task_status,
)

router = APIRouter(prefix="/projects", tags=["projects"])


# ─── 프로젝트 엔드포인트 ─────────────────────────────────────


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project_endpoint(
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """프로젝트 생성"""
    project = await create_project(db, current_user.id, data)
    return project


@router.get("/", response_model=list[ProjectResponse])
async def list_projects_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """내 프로젝트 목록"""
    return await get_user_projects(db, current_user.id)


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project_endpoint(
    project_id: int,
    member: ProjectMember = Depends(get_project_member),
    db: AsyncSession = Depends(get_db),
):
    """프로젝트 상세 (멤버 목록 포함)"""
    project = await get_project_by_id(db, project_id)
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project_endpoint(
    project_id: int,
    data: ProjectUpdate,
    member: ProjectMember = Depends(get_project_member),
    db: AsyncSession = Depends(get_db),
):
    """프로젝트 수정 (owner/admin만)"""
    if member.role not in (ProjectRole.owner, ProjectRole.admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="프로젝트 수정 권한이 없습니다.",
        )
    project = await get_project_by_id(db, project_id)
    return await update_project(db, project, data)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_endpoint(
    project_id: int,
    member: ProjectMember = Depends(get_project_member),
    db: AsyncSession = Depends(get_db),
):
    """프로젝트 삭제 (owner만)"""
    if member.role != ProjectRole.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="프로젝트 삭제 권한이 없습니다.",
        )
    # members를 eager load하지 않고 단순 조회 (CASCADE 충돌 방지)
    from sqlalchemy import delete as sql_delete

    from app.models.project import Project

    await db.execute(sql_delete(Project).where(Project.id == project_id))
    await db.flush()


@router.post(
    "/{project_id}/members",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_member_endpoint(
    project_id: int,
    data: ProjectMemberAdd,
    member: ProjectMember = Depends(get_project_member),
    db: AsyncSession = Depends(get_db),
):
    """멤버 추가 (owner/admin만)"""
    if member.role not in (ProjectRole.owner, ProjectRole.admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="멤버 추가 권한이 없습니다.",
        )
    return await add_project_member(db, project_id, data.user_id, data.role)


# ─── 태스크 엔드포인트 ─────────────────────────────────────


@router.post(
    "/{project_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task_endpoint(
    project_id: int,
    data: TaskCreate,
    member: ProjectMember = Depends(get_project_member),
    db: AsyncSession = Depends(get_db),
):
    """태스크 생성"""
    return await create_task(db, project_id, data)


@router.get("/{project_id}/tasks", response_model=list[TaskResponse])
async def list_tasks_endpoint(
    project_id: int,
    member: ProjectMember = Depends(get_project_member),
    db: AsyncSession = Depends(get_db),
    task_status: TaskStatus | None = Query(None, alias="status"),
    priority: TaskPriority | None = None,
    assignee_id: int | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
):
    """태스크 목록 (필터/정렬)"""
    return await get_tasks(
        db,
        project_id,
        status=task_status,
        priority=priority,
        assignee_id=assignee_id,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/{project_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task_endpoint(
    project_id: int,
    task_id: int,
    member: ProjectMember = Depends(get_project_member),
    db: AsyncSession = Depends(get_db),
):
    """태스크 상세"""
    task = await get_task_by_id(db, task_id, project_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="태스크를 찾을 수 없습니다.",
        )
    return task


@router.put("/{project_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task_endpoint(
    project_id: int,
    task_id: int,
    data: TaskUpdate,
    member: ProjectMember = Depends(get_project_member),
    db: AsyncSession = Depends(get_db),
):
    """태스크 수정"""
    task = await get_task_by_id(db, task_id, project_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="태스크를 찾을 수 없습니다.",
        )
    return await update_task(db, task, data)


@router.patch("/{project_id}/tasks/{task_id}/status", response_model=TaskResponse)
async def update_task_status_endpoint(
    project_id: int,
    task_id: int,
    data: TaskStatusUpdate,
    member: ProjectMember = Depends(get_project_member),
    db: AsyncSession = Depends(get_db),
):
    """태스크 상태 변경"""
    task = await get_task_by_id(db, task_id, project_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="태스크를 찾을 수 없습니다.",
        )
    return await update_task_status(db, task, data)


@router.delete("/{project_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_endpoint(
    project_id: int,
    task_id: int,
    member: ProjectMember = Depends(get_project_member),
    db: AsyncSession = Depends(get_db),
):
    """태스크 삭제"""
    task = await get_task_by_id(db, task_id, project_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="태스크를 찾을 수 없습니다.",
        )
    await delete_task(db, task)


# ─── 댓글 엔드포인트 ─────────────────────────────────────


@router.post(
    "/{project_id}/tasks/{task_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment_endpoint(
    project_id: int,
    task_id: int,
    data: CommentCreate,
    member: ProjectMember = Depends(get_project_member),
    db: AsyncSession = Depends(get_db),
):
    """댓글 생성"""
    task = await get_task_by_id(db, task_id, project_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="태스크를 찾을 수 없습니다.",
        )
    return await create_comment(db, task_id, member.user_id, data)


@router.get(
    "/{project_id}/tasks/{task_id}/comments",
    response_model=list[CommentResponse],
)
async def list_comments_endpoint(
    project_id: int,
    task_id: int,
    member: ProjectMember = Depends(get_project_member),
    db: AsyncSession = Depends(get_db),
):
    """댓글 목록"""
    task = await get_task_by_id(db, task_id, project_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="태스크를 찾을 수 없습니다.",
        )
    return await get_task_comments(db, task_id)

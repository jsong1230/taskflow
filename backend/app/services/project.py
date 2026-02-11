from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project import Project, ProjectMember, ProjectRole
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate


async def create_project(
    db: AsyncSession,
    owner_id: int,
    data: ProjectCreate,
) -> Project:
    """프로젝트 생성 + owner 멤버십 자동 추가"""
    project = Project(
        name=data.name,
        description=data.description,
        owner_id=owner_id,
    )
    db.add(project)
    await db.flush()

    # owner 멤버십 자동 추가
    member = ProjectMember(
        user_id=owner_id,
        project_id=project.id,
        role=ProjectRole.owner,
    )
    db.add(member)
    await db.flush()
    await db.refresh(project)

    return project


async def get_user_projects(
    db: AsyncSession,
    user_id: int,
) -> list[Project]:
    """사용자가 멤버인 프로젝트 목록"""
    result = await db.execute(
        select(Project)
        .join(ProjectMember, ProjectMember.project_id == Project.id)
        .where(ProjectMember.user_id == user_id)
        .order_by(Project.created_at.desc())
    )
    return list(result.scalars().all())


async def get_project_by_id(
    db: AsyncSession,
    project_id: int,
) -> Project | None:
    """ID로 프로젝트 조회 (members eager load)"""
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.members))
        .where(Project.id == project_id)
    )
    return result.scalar_one_or_none()


async def update_project(
    db: AsyncSession,
    project: Project,
    data: ProjectUpdate,
) -> Project:
    """프로젝트 수정 (partial update)"""
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    await db.flush()
    await db.refresh(project)
    return project


async def delete_project(
    db: AsyncSession,
    project: Project,
) -> None:
    """프로젝트 삭제"""
    await db.delete(project)
    await db.flush()


async def add_project_member(
    db: AsyncSession,
    project_id: int,
    user_id: int,
    role: ProjectRole,
) -> ProjectMember:
    """멤버 추가 (중복/존재여부 체크)"""
    # 사용자 존재 확인
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다.",
        )

    # 중복 멤버십 확인
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 프로젝트 멤버입니다.",
        )

    member = ProjectMember(
        user_id=user_id,
        project_id=project_id,
        role=role,
    )
    db.add(member)
    await db.flush()
    await db.refresh(member)
    return member

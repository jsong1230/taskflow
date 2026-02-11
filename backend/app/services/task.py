from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskStatusUpdate, TaskUpdate


async def create_task(
    db: AsyncSession,
    project_id: int,
    data: TaskCreate,
) -> Task:
    """태스크 생성"""
    task = Task(
        title=data.title,
        description=data.description,
        priority=data.priority,
        assignee_id=data.assignee_id,
        project_id=project_id,
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task


async def get_tasks(
    db: AsyncSession,
    project_id: int,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    assignee_id: int | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> list[Task]:
    """태스크 목록 조회 (동적 WHERE + ORDER BY)"""
    query = select(Task).where(Task.project_id == project_id)

    if status is not None:
        query = query.where(Task.status == status)
    if priority is not None:
        query = query.where(Task.priority == priority)
    if assignee_id is not None:
        query = query.where(Task.assignee_id == assignee_id)

    # 정렬
    allowed_sort_fields = {"created_at", "updated_at", "title", "priority", "status"}
    if sort_by not in allowed_sort_fields:
        sort_by = "created_at"

    sort_column = getattr(Task, sort_by)
    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_task_by_id(
    db: AsyncSession,
    task_id: int,
    project_id: int,
) -> Task | None:
    """태스크 조회 (project_id 일치 확인)"""
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.project_id == project_id)
    )
    return result.scalar_one_or_none()


async def update_task(
    db: AsyncSession,
    task: Task,
    data: TaskUpdate,
) -> Task:
    """태스크 수정"""
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    await db.flush()
    await db.refresh(task)
    return task


async def update_task_status(
    db: AsyncSession,
    task: Task,
    data: TaskStatusUpdate,
) -> Task:
    """태스크 상태 변경"""
    task.status = data.status
    await db.flush()
    await db.refresh(task)
    return task


async def delete_task(
    db: AsyncSession,
    task: Task,
) -> None:
    """태스크 삭제"""
    await db.delete(task)
    await db.flush()

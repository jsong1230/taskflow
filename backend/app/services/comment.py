from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.schemas.comment import CommentCreate


async def create_comment(
    db: AsyncSession,
    task_id: int,
    author_id: int,
    data: CommentCreate,
) -> Comment:
    """댓글 생성"""
    comment = Comment(
        content=data.content,
        task_id=task_id,
        author_id=author_id,
    )
    db.add(comment)
    await db.flush()
    await db.refresh(comment)
    return comment


async def get_task_comments(
    db: AsyncSession,
    task_id: int,
) -> list[Comment]:
    """댓글 목록 (created_at ASC)"""
    result = await db.execute(
        select(Comment)
        .where(Comment.task_id == task_id)
        .order_by(Comment.created_at.asc())
    )
    return list(result.scalars().all())

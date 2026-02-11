from datetime import datetime

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    projects_owned = relationship("Project", back_populates="owner")
    project_memberships = relationship("ProjectMember", back_populates="user")
    assigned_tasks = relationship("Task", back_populates="assignee")
    comments = relationship("Comment", back_populates="author")

import enum
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProjectRole(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    member = "member"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String(2000), default="")
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    owner = relationship("User", back_populates="projects_owned")
    members = relationship("ProjectMember", back_populates="project")
    tasks = relationship("Task", back_populates="project")


class ProjectMember(Base):
    __tablename__ = "project_members"
    __table_args__ = (
        UniqueConstraint("user_id", "project_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE")
    )
    role: Mapped[ProjectRole] = mapped_column(
        Enum(ProjectRole, native_enum=False),
        default=ProjectRole.member,
    )

    user = relationship("User", back_populates="project_memberships")
    project = relationship("Project", back_populates="members")

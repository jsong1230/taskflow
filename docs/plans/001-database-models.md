# 백엔드 데이터베이스 모델 구현 계획

**상태**: 완료
**작성일**: 2026-02-11

## Context

TaskFlow 백엔드에 핵심 데이터베이스 모델(User, Project, ProjectMember, Task, Comment)을 추가한다. 현재 `app/core/database.py`에 SQLAlchemy 2.0 `DeclarativeBase`가 정의되어 있고, Alembic이 async 템플릿으로 초기화되어 있으나 마이그레이션은 아직 없다.

---

## 파일 변경 목록

### 새로 생성 (4개)
| 파일 | 설명 |
|------|------|
| `backend/app/models/user.py` | User 모델 |
| `backend/app/models/project.py` | Project + ProjectMember 모델 |
| `backend/app/models/task.py` | Task 모델 |
| `backend/app/models/comment.py` | Comment 모델 |

### 수정 (1개)
| 파일 | 변경 내용 |
|------|-----------|
| `backend/app/models/__init__.py` | 모든 모델 import 추가 (Alembic autogenerate 인식용) |

### 자동 생성 (1개)
| 파일 | 설명 |
|------|------|
| `backend/alembic/versions/6aafea0ccb93_add_initial_models.py` | 마이그레이션 파일 (수동 작성) |

---

## 모델 설계

### Enum 정의 (각 모델 파일 내 Python `enum.Enum`)
- `ProjectRole`: `owner`, `admin`, `member`
- `TaskStatus`: `todo`, `in_progress`, `done`
- `TaskPriority`: `low`, `medium`, `high`, `critical`
- DB에 `native_enum=False` (VARCHAR 저장) — PostgreSQL enum 타입의 마이그레이션 복잡성 회피

### User (`app/models/user.py`)
```
테이블: users
- id: Mapped[int] (PK)
- email: Mapped[str] (unique, index)
- hashed_password: Mapped[str]
- name: Mapped[str]
- created_at: Mapped[datetime] (server_default=func.now())
- relationships: projects_owned, project_memberships, assigned_tasks, comments
```

### Project (`app/models/project.py`)
```
테이블: projects
- id: Mapped[int] (PK)
- name: Mapped[str]
- description: Mapped[str] (default="")
- owner_id: Mapped[int] (FK→users.id, ondelete=CASCADE)
- created_at: Mapped[datetime] (server_default=func.now())
- relationships: owner, members, tasks
```

### ProjectMember (`app/models/project.py`)
```
테이블: project_members
- id: Mapped[int] (PK)
- user_id: Mapped[int] (FK→users.id, ondelete=CASCADE)
- project_id: Mapped[int] (FK→projects.id, ondelete=CASCADE)
- role: Mapped[ProjectRole] (default=member)
- UniqueConstraint(user_id, project_id)
- relationships: user, project
```

### Task (`app/models/task.py`)
```
테이블: tasks
- id: Mapped[int] (PK)
- title: Mapped[str]
- description: Mapped[str] (default="")
- status: Mapped[TaskStatus] (default=todo)
- priority: Mapped[TaskPriority] (default=medium)
- project_id: Mapped[int] (FK→projects.id, ondelete=CASCADE)
- assignee_id: Mapped[int | None] (FK→users.id, ondelete=SET NULL, nullable)
- created_at: Mapped[datetime] (server_default=func.now())
- updated_at: Mapped[datetime] (server_default=func.now(), onupdate=func.now())
- relationships: project, assignee, comments
```

### Comment (`app/models/comment.py`)
```
테이블: comments
- id: Mapped[int] (PK)
- content: Mapped[str] (Text)
- task_id: Mapped[int] (FK→tasks.id, ondelete=CASCADE)
- author_id: Mapped[int] (FK→users.id, ondelete=CASCADE)
- created_at: Mapped[datetime] (server_default=func.now())
- relationships: task, author
```

---

## 마이그레이션

Docker가 실행되지 않아 autogenerate 대신 `alembic revision -m "add initial models"`로 빈 파일을 생성한 뒤 수동으로 작성했다.

마이그레이션 파일: `backend/alembic/versions/6aafea0ccb93_add_initial_models.py`

---

## 검증 결과

1. 모든 모델 import 성공 (경고 없음)
2. `pytest -v` — 기존 health 테스트 통과 (1 passed)
3. 마이그레이션 파일 내용: 5개 테이블 CREATE/DROP 정의 완료

## 구현 시 참고사항

- `native_enum=False`는 `mapped_column()`이 아닌 `Enum()` 타입 인자로 전달해야 SAWarning이 발생하지 않음
- Docker 없이 마이그레이션 생성 시 autogenerate 불가 → 수동 작성 필요

# TaskFlow 개발 가이드

## 목차
- [로컬 개발 환경 설정](#로컬-개발-환경-설정)
- [백엔드 개발](#백엔드-개발)
- [프론트엔드 개발](#프론트엔드-개발)
- [데이터베이스 관리](#데이터베이스-관리)
- [테스트](#테스트)
- [코딩 컨벤션](#코딩-컨벤션)
- [Git 워크플로우](#git-워크플로우)
- [디버깅](#디버깅)
- [트러블슈팅](#트러블슈팅)

---

## 로컬 개발 환경 설정

### 사전 요구사항

- **Python 3.12+** (백엔드)
- **Node.js 18+** (프론트엔드)
- **PostgreSQL 16** (데이터베이스)
- **Docker & Docker Compose** (선택, 컨테이너 개발 환경)

### Docker Compose를 이용한 빠른 시작 (권장)

```bash
# 1. 저장소 클론
git clone https://github.com/your-username/taskflow.git
cd taskflow

# 2. 환경변수 설정
cp .env.example .env
# .env 파일을 열어서 필요한 값 수정

# 3. Docker Compose로 모든 서비스 실행
docker-compose up -d

# 4. 데이터베이스 마이그레이션
docker-compose exec backend alembic upgrade head

# 5. 접속 확인
# - 백엔드 API: http://localhost:8000
# - 프론트엔드: http://localhost:3000
# - Swagger UI: http://localhost:8000/docs
```

### 로컬 환경 설정 (Docker 없이)

#### 1. PostgreSQL 설치 및 실행

**macOS (Homebrew)**
```bash
brew install postgresql@16
brew services start postgresql@16

# 데이터베이스 및 사용자 생성
psql postgres
CREATE DATABASE taskflow;
CREATE USER taskflow WITH PASSWORD 'taskflow_secret';
GRANT ALL PRIVILEGES ON DATABASE taskflow TO taskflow;
\q
```

**Ubuntu/Debian**
```bash
sudo apt update
sudo apt install postgresql-16
sudo systemctl start postgresql

sudo -u postgres psql
CREATE DATABASE taskflow;
CREATE USER taskflow WITH PASSWORD 'taskflow_secret';
GRANT ALL PRIVILEGES ON DATABASE taskflow TO taskflow;
\q
```

#### 2. 백엔드 설정

```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정 (프로젝트 루트의 .env 파일 사용)
cd ..
cp .env.example .env
# .env 파일 편집하여 DATABASE_URL 등 설정

# 데이터베이스 마이그레이션
cd backend
alembic upgrade head

# 개발 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. 프론트엔드 설정

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 빌드 (프로덕션)
npm run build
npm run start
```

---

## 백엔드 개발

### 디렉토리 구조

```
backend/
├── app/
│   ├── api/              # API 라우터
│   │   └── v1/
│   │       ├── auth.py       # 인증 API
│   │       ├── projects.py   # 프로젝트/태스크/댓글 API
│   │       └── health.py     # 헬스체크
│   ├── core/             # 핵심 설정
│   │   ├── config.py         # 환경변수 설정
│   │   ├── database.py       # DB 연결 및 세션
│   │   ├── security.py       # JWT, 비밀번호 해싱
│   │   └── dependencies.py   # FastAPI Depends
│   ├── models/           # SQLAlchemy 모델
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── task.py
│   │   └── comment.py
│   ├── schemas/          # Pydantic 스키마
│   │   ├── user.py
│   │   ├── auth.py
│   │   ├── project.py
│   │   ├── task.py
│   │   └── comment.py
│   ├── services/         # 비즈니스 로직
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── task.py
│   │   └── comment.py
│   ├── tests/            # 테스트
│   │   ├── conftest.py       # pytest fixtures
│   │   ├── test_auth.py
│   │   ├── test_projects.py
│   │   └── test_tasks.py
│   └── main.py           # FastAPI 앱 엔트리포인트
├── alembic/              # 마이그레이션
│   └── versions/
├── requirements.txt
└── alembic.ini
```

### 새로운 엔드포인트 추가

#### 1. 모델 정의 (models/)

```python
# app/models/example.py
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Example(Base):
    __tablename__ = "examples"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
```

#### 2. 스키마 정의 (schemas/)

```python
# app/schemas/example.py
from pydantic import BaseModel, ConfigDict

class ExampleCreate(BaseModel):
    name: str

class ExampleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
```

#### 3. 서비스 로직 (services/)

```python
# app/services/example.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.example import Example
from app.schemas.example import ExampleCreate

async def create_example(db: AsyncSession, data: ExampleCreate) -> Example:
    example = Example(name=data.name)
    db.add(example)
    await db.flush()
    await db.refresh(example)
    return example

async def get_examples(db: AsyncSession) -> list[Example]:
    result = await db.execute(select(Example))
    return result.scalars().all()
```

#### 4. API 엔드포인트 (api/v1/)

```python
# app/api/v1/examples.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user
from app.schemas.example import ExampleCreate, ExampleResponse
from app.services.example import create_example, get_examples

router = APIRouter(prefix="/examples", tags=["examples"])

@router.post("/", response_model=ExampleResponse)
async def create_example_endpoint(
    data: ExampleCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return await create_example(db, data)

@router.get("/", response_model=list[ExampleResponse])
async def list_examples_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return await get_examples(db)
```

#### 5. 라우터 등록 (main.py)

```python
# app/main.py
from app.api.v1 import examples

app.include_router(examples.router, prefix="/api/v1")
```

### 환경변수 관리

환경변수는 프로젝트 루트의 `.env` 파일에서 관리합니다.

```bash
# .env
DATABASE_URL=postgresql+asyncpg://taskflow:taskflow_secret@localhost:5432/taskflow
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

환경변수는 `app/core/config.py`의 `Settings` 클래스에서 자동으로 로드됩니다.

---

## 프론트엔드 개발

### 디렉토리 구조

```
frontend/
├── app/                  # Next.js App Router
│   ├── page.tsx              # 홈페이지
│   ├── layout.tsx            # 전역 레이아웃
│   ├── login/
│   │   └── page.tsx          # 로그인 페이지
│   ├── register/
│   │   └── page.tsx          # 회원가입 페이지
│   ├── dashboard/
│   │   └── page.tsx          # 대시보드
│   └── projects/
│       ├── page.tsx          # 프로젝트 목록
│       └── [id]/
│           └── page.tsx      # 칸반 보드
├── components/           # React 컴포넌트
│   ├── ProtectedRoute.tsx
│   ├── kanban/
│   │   ├── KanbanBoard.tsx
│   │   ├── KanbanColumn.tsx
│   │   ├── TaskCard.tsx
│   │   ├── TaskDetailModal.tsx
│   │   ├── CreateTaskForm.tsx
│   │   └── CommentSection.tsx
│   └── dashboard/
│       ├── ProjectStatsCard.tsx
│       ├── ProgressBar.tsx
│       └── AssignedTasksList.tsx
├── contexts/             # React Context
│   └── AuthContext.tsx       # 인증 상태 관리
├── lib/                  # 유틸리티
│   └── api.ts                # API 클라이언트
├── types/                # TypeScript 타입
│   ├── api.ts                # API 응답 타입
│   └── index.ts
├── public/               # 정적 파일
├── package.json
└── tsconfig.json
```

### 새로운 페이지 추가

Next.js 15의 App Router를 사용합니다.

```typescript
// app/new-page/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';

export default function NewPage() {
  const { user } = useAuth();
  const [data, setData] = useState(null);

  useEffect(() => {
    // 데이터 fetching
  }, []);

  return (
    <div>
      <h1>New Page</h1>
      {user && <p>안녕하세요, {user.name}님!</p>}
    </div>
  );
}
```

### API 호출

프론트엔드에서 백엔드 API를 호출할 때는 `lib/api.ts`의 함수를 사용합니다.

```typescript
import { projectApi, taskApi } from '@/lib/api';

// 프로젝트 목록 조회
const projects = await projectApi.list();

// 태스크 생성
const newTask = await taskApi.create(projectId, {
  title: '새 태스크',
  description: '설명',
  priority: 'high',
});
```

### 컴포넌트 작성 규칙

```typescript
// components/example/ExampleComponent.tsx
'use client';  // 클라이언트 상태가 필요한 경우

import { useState } from 'react';

interface ExampleComponentProps {
  title: string;
  count?: number;
  onAction?: () => void;
}

export default function ExampleComponent({
  title,
  count = 0,
  onAction,
}: ExampleComponentProps) {
  const [value, setValue] = useState(count);

  return (
    <div className="rounded-lg border p-4">
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="text-gray-600">{value}</p>
      {onAction && (
        <button
          onClick={onAction}
          className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Action
        </button>
      )}
    </div>
  );
}
```

---

## 데이터베이스 관리

### Alembic 마이그레이션

#### 새로운 마이그레이션 생성

모델을 수정한 후 마이그레이션을 생성합니다.

```bash
cd backend

# 자동으로 마이그레이션 생성 (모델 변경사항 감지)
alembic revision --autogenerate -m "add new column to task"

# 수동으로 빈 마이그레이션 생성
alembic revision -m "custom migration"
```

생성된 파일은 `backend/alembic/versions/` 디렉토리에 있습니다.

#### 마이그레이션 적용

```bash
# 최신 버전으로 업그레이드
alembic upgrade head

# 특정 버전으로 업그레이드
alembic upgrade <revision_id>

# 한 단계 업그레이드
alembic upgrade +1

# 한 단계 다운그레이드
alembic downgrade -1

# 마이그레이션 히스토리 확인
alembic history

# 현재 버전 확인
alembic current
```

#### 마이그레이션 파일 예시

```python
# alembic/versions/abc123_add_due_date_to_task.py
from alembic import op
import sqlalchemy as sa

revision = 'abc123'
down_revision = 'xyz789'

def upgrade():
    op.add_column('tasks', sa.Column('due_date', sa.Date(), nullable=True))

def downgrade():
    op.drop_column('tasks', 'due_date')
```

### 데이터베이스 직접 접근

```bash
# PostgreSQL 접속 (Docker Compose 사용 시)
docker-compose exec db psql -U taskflow -d taskflow

# 로컬 PostgreSQL 접속
psql -U taskflow -d taskflow

# 테이블 목록 확인
\dt

# 테이블 스키마 확인
\d tasks

# SQL 실행
SELECT * FROM tasks WHERE status = 'todo';
```

### 데이터베이스 초기화 (개발 환경)

```bash
# 모든 마이그레이션 롤백
alembic downgrade base

# 다시 적용
alembic upgrade head

# 또는 데이터베이스 삭제 후 재생성 (Docker Compose)
docker-compose down -v
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

---

## 테스트

### 백엔드 테스트 (pytest)

#### 테스트 실행

```bash
cd backend

# 모든 테스트 실행
pytest

# 특정 파일 실행
pytest tests/test_auth.py

# 특정 테스트 함수 실행
pytest tests/test_auth.py::test_register

# 커버리지 포함
pytest --cov=app --cov-report=html

# 커버리지 리포트 확인 (브라우저)
open htmlcov/index.html
```

#### 테스트 작성

```python
# tests/test_example.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_example():
    """Example 생성 테스트"""
    response = client.post(
        "/api/v1/examples/",
        json={"name": "Test Example"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Example"

def test_create_example_unauthorized():
    """인증 없이 Example 생성 시도"""
    response = client.post(
        "/api/v1/examples/",
        json={"name": "Test Example"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_async_function():
    """비동기 함수 테스트"""
    result = await some_async_function()
    assert result is not None
```

#### Fixtures 사용

```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.database import Base

@pytest.fixture
async def db_session():
    """테스트용 데이터베이스 세션"""
    engine = create_async_engine("postgresql+asyncpg://...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def auth_token(client, db_session):
    """인증 토큰 생성"""
    # 사용자 생성 및 로그인
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    return response.json()["token"]["access_token"]
```

### 프론트엔드 테스트

현재 프론트엔드 테스트는 구현되지 않았습니다. 추후 Jest + React Testing Library를 이용하여 추가할 예정입니다.

---

## 코딩 컨벤션

### 백엔드 (Python/FastAPI)

#### PEP 8 스타일 가이드 준수

```python
# Good
def get_user_by_id(user_id: int) -> User | None:
    pass

# Bad
def getUserById(userId):
    pass
```

#### Type Hints 필수

```python
# Good
async def create_task(
    db: AsyncSession,
    project_id: int,
    data: TaskCreate
) -> Task:
    pass

# Bad
async def create_task(db, project_id, data):
    pass
```

#### 명명 규칙

- 함수/변수: `snake_case`
- 클래스: `PascalCase`
- 상수: `UPPER_SNAKE_CASE`

#### Docstring 작성

```python
async def update_task_status(
    db: AsyncSession,
    task: Task,
    data: TaskStatusUpdate
) -> Task:
    """
    태스크 상태를 변경합니다.

    Args:
        db: 데이터베이스 세션
        task: 수정할 태스크 객체
        data: 새로운 상태 정보

    Returns:
        Task: 수정된 태스크

    Raises:
        ValueError: 유효하지 않은 상태값
    """
    task.status = data.status
    await db.flush()
    await db.refresh(task)
    return task
```

### 프론트엔드 (TypeScript/Next.js)

#### ESLint + Prettier 사용

```bash
# 코드 검사
npm run lint

# 코드 자동 포맷팅 (Prettier는 저장 시 자동 적용)
npm run lint -- --fix
```

#### 명명 규칙

- 컴포넌트/타입/인터페이스: `PascalCase`
- 함수/변수: `camelCase`
- 상수: `UPPER_SNAKE_CASE`

```typescript
// Good
interface TaskCardProps {
  taskId: number;
  onDelete: () => void;
}

const API_BASE_URL = 'http://localhost:8000';

function TaskCard({ taskId, onDelete }: TaskCardProps) {
  const [isLoading, setIsLoading] = useState(false);
  // ...
}

// Bad
interface taskCardProps {
  TaskId: number;
}
```

#### Server Components vs Client Components

```typescript
// Server Component (기본값, 'use client' 없음)
// - 서버에서 렌더링
// - useState, useEffect 등 사용 불가
export default async function ProjectList() {
  const projects = await fetch('...');
  return <div>{/* ... */}</div>;
}

// Client Component ('use client' 명시)
// - 클라이언트에서 렌더링
// - useState, useEffect, onClick 등 사용 가능
'use client';
export default function TaskCard({ task }) {
  const [isOpen, setIsOpen] = useState(false);
  return <div onClick={() => setIsOpen(true)}>{/* ... */}</div>;
}
```

---

## Git 워크플로우

### Conventional Commits

커밋 메시지는 다음 형식을 따릅니다:

```
<type>: <subject>

<body (optional)>

<footer (optional)>
```

**Type**
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `refactor`: 코드 리팩토링
- `docs`: 문서 수정
- `test`: 테스트 추가/수정
- `chore`: 빌드, 설정 파일 수정
- `style`: 코드 포맷팅, 세미콜론 누락 등

**예시**
```
feat: 칸반 보드에 드래그 앤 드롭 기능 추가

- HTML5 Drag and Drop API 사용
- 낙관적 업데이트로 UX 개선
- 에러 발생 시 롤백 처리

Closes #23
```

```
fix: 태스크 삭제 시 댓글이 함께 삭제되지 않는 버그 수정

CASCADE 삭제 옵션을 Comment 모델에 추가했습니다.
```

### 브랜치 전략

```bash
# 새로운 기능 개발
git checkout -b feat/kanban-drag-drop

# 버그 수정
git checkout -b fix/task-deletion-bug

# 리팩토링
git checkout -b refactor/auth-middleware

# 작업 완료 후 커밋
git add .
git commit -m "feat: add drag and drop to kanban board"

# 푸시
git push origin feat/kanban-drag-drop
```

### Pull Request

1. 브랜치 생성 및 작업
2. 커밋 및 푸시
3. GitHub에서 Pull Request 생성
4. 코드 리뷰
5. 승인 후 `master` 브랜치로 Merge

---

## 디버깅

### 백엔드 디버깅

#### 로깅

```python
import logging

logger = logging.getLogger(__name__)

async def some_function():
    logger.info("Function started")
    logger.debug(f"Variable value: {variable}")
    try:
        # ...
    except Exception as e:
        logger.error(f"Error occurred: {e}", exc_info=True)
```

#### VSCode 디버거 설정

`.vscode/launch.json`
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "cwd": "${workspaceFolder}/backend",
      "jinja": true
    }
  ]
}
```

#### 데이터베이스 쿼리 로깅

```python
# app/core/database.py
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### 프론트엔드 디버깅

#### 브라우저 개발자 도구

- **Console**: `console.log()`, `console.error()`
- **Network**: API 요청/응답 확인
- **React DevTools**: 컴포넌트 상태 확인

#### VSCode 디버거 설정

`.vscode/launch.json`
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Next.js: debug client-side",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:3000",
      "webRoot": "${workspaceFolder}/frontend"
    }
  ]
}
```

---

## 트러블슈팅

### 자주 발생하는 문제

#### 1. 백엔드 서버가 시작되지 않음

**증상**: `ModuleNotFoundError` 또는 `ImportError`

**해결**:
```bash
cd backend
pip install -r requirements.txt
```

**증상**: `Connection refused` (데이터베이스)

**해결**:
```bash
# PostgreSQL이 실행 중인지 확인
docker-compose ps db
# 또는
pg_isready -U taskflow

# Docker Compose 재시작
docker-compose restart db
```

#### 2. 마이그레이션 오류

**증상**: `alembic.util.exc.CommandError: Target database is not up to date`

**해결**:
```bash
# 현재 버전 확인
alembic current

# 최신 버전으로 업그레이드
alembic upgrade head
```

**증상**: 마이그레이션 충돌

**해결**:
```bash
# 마이그레이션 히스토리 확인
alembic history

# 문제 있는 마이그레이션 파일 수정 또는 삭제
# 그 후 다시 생성
alembic revision --autogenerate -m "fix migration"
```

#### 3. 프론트엔드 빌드 오류

**증상**: `Module not found` 또는 `Cannot find module`

**해결**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**증상**: `CORS policy` 오류

**해결**:
- 백엔드 `.env` 파일에서 `BACKEND_CORS_ORIGINS` 확인
- 프론트엔드 URL이 포함되어 있는지 확인

#### 4. JWT 토큰 오류

**증상**: `401 Unauthorized` 또는 `Invalid token`

**해결**:
- 토큰이 올바르게 로컬스토리지에 저장되었는지 확인
- 토큰 만료 여부 확인 (30분)
- 다시 로그인

```typescript
// 브라우저 콘솔에서 토큰 확인
localStorage.getItem('access_token');

// 토큰 삭제 후 재로그인
localStorage.removeItem('access_token');
```

#### 5. Docker Compose 포트 충돌

**증상**: `port is already allocated`

**해결**:
```bash
# 포트 사용 중인 프로세스 찾기
lsof -i :8000  # 백엔드
lsof -i :3000  # 프론트엔드
lsof -i :5433  # PostgreSQL

# 프로세스 종료
kill -9 <PID>

# 또는 docker-compose.yml에서 포트 변경
```

#### 6. 데이터베이스 연결 풀 부족

**증상**: `QueuePool limit of size X overflow Y reached`

**해결**:
```python
# app/core/database.py
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,       # 기본 연결 수 증가
    max_overflow=40,    # 오버플로우 증가
)
```

---

## 추가 자료

### 공식 문서

- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/en/20/
- **Alembic**: https://alembic.sqlalchemy.org/
- **Next.js 15**: https://nextjs.org/docs
- **Tailwind CSS**: https://tailwindcss.com/docs

### 유용한 도구

- **Postman**: API 테스트
- **pgAdmin**: PostgreSQL GUI 클라이언트
- **DB Viewer (VSCode Extension)**: 데이터베이스 뷰어

---

## 문의

버그 제보 또는 기능 제안은 GitHub Issues에 등록해주세요.

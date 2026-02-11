# TaskFlow 아키텍처 문서

## 목차
- [시스템 개요](#시스템-개요)
- [시스템 아키텍처](#시스템-아키텍처)
- [백엔드 아키텍처](#백엔드-아키텍처)
- [프론트엔드 아키텍처](#프론트엔드-아키텍처)
- [데이터베이스 스키마](#데이터베이스-스키마)
- [API 설계 철학](#api-설계-철학)
- [인증 및 인가](#인증-및-인가)
- [드래그 앤 드롭 구현](#드래그-앤-드롭-구현)
- [기술 결정사항](#기술-결정사항)
- [보안 고려사항](#보안-고려사항)
- [확장성 고려사항](#확장성-고려사항)

---

## 시스템 개요

TaskFlow는 팀 협업을 위한 칸반 보드 기반 태스크 관리 웹 애플리케이션입니다.

**핵심 기능**
- 사용자 인증 및 권한 관리
- 프로젝트 생성 및 멤버 관리
- 칸반 보드 (Todo, In Progress, Done)
- 드래그 앤 드롭으로 태스크 상태 변경
- 태스크 필터링 및 정렬
- 태스크 댓글 시스템
- 대시보드 (프로젝트 현황 요약)

**기술 스택**
- **백엔드**: FastAPI (Python 3.12) + SQLAlchemy 2.0 + PostgreSQL 16
- **프론트엔드**: Next.js 15 (App Router) + TypeScript + Tailwind CSS
- **인증**: JWT (JSON Web Token)
- **컨테이너화**: Docker + Docker Compose

---

## 시스템 아키텍처

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────────────────────────────────────┐
│              Nginx (Reverse Proxy)          │
│  - SSL/TLS Termination                      │
│  - Static File Serving                      │
│  - Load Balancing                           │
└──────┬─────────────────────┬────────────────┘
       │                     │
       │ /api/               │ /
       ▼                     ▼
┌──────────────┐      ┌─────────────┐
│   Backend    │      │  Frontend   │
│   (FastAPI)  │◄─────┤  (Next.js)  │
└──────┬───────┘      └─────────────┘
       │
       │ SQLAlchemy
       ▼
┌──────────────┐
│  PostgreSQL  │
│   Database   │
└──────────────┘
```

### 통신 흐름

1. **클라이언트 → Nginx**: 브라우저에서 HTTPS 요청
2. **Nginx → Frontend**: Next.js 앱 (정적 파일 + SSR)
3. **Frontend → Backend**: API 호출 (JWT 토큰 포함)
4. **Backend → Database**: SQLAlchemy를 통한 비동기 쿼리
5. **Backend → Frontend**: JSON 응답
6. **Frontend → 클라이언트**: 렌더링된 HTML

---

## 백엔드 아키텍처

### 레이어 구조

TaskFlow 백엔드는 계층형 아키텍처를 따릅니다.

```
┌──────────────────────────────────────┐
│       API Layer (FastAPI)            │  ← HTTP 요청/응답 처리
│  - Route 정의                        │
│  - Request Validation (Pydantic)     │
│  - Response Serialization            │
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│      Service Layer (Business Logic)  │  ← 비즈니스 로직
│  - 트랜잭션 관리                     │
│  - 권한 검증                         │
│  - 데이터 가공                       │
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│       Data Layer (SQLAlchemy ORM)    │  ← 데이터 접근
│  - 모델 정의                         │
│  - 데이터베이스 쿼리                 │
│  - 관계 매핑                         │
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│         PostgreSQL Database          │  ← 데이터 저장소
└──────────────────────────────────────┘
```

### 디렉토리 구조

```
backend/app/
├── api/                    # API Layer
│   └── v1/
│       ├── auth.py         # 인증 엔드포인트
│       ├── projects.py     # 프로젝트/태스크/댓글 엔드포인트
│       └── health.py       # 헬스체크
│
├── core/                   # 핵심 설정 및 유틸리티
│   ├── config.py           # 환경변수 (Pydantic Settings)
│   ├── database.py         # DB 연결 및 세션 관리
│   ├── security.py         # JWT, 비밀번호 해싱
│   └── dependencies.py     # FastAPI Depends (DI)
│
├── models/                 # Data Layer (SQLAlchemy Models)
│   ├── user.py             # User 모델
│   ├── project.py          # Project, ProjectMember 모델
│   ├── task.py             # Task 모델
│   └── comment.py          # Comment 모델
│
├── schemas/                # Pydantic Schemas (Validation)
│   ├── user.py
│   ├── auth.py
│   ├── project.py
│   ├── task.py
│   └── comment.py
│
├── services/               # Service Layer (Business Logic)
│   ├── user.py             # 사용자 관리 로직
│   ├── project.py          # 프로젝트 관리 로직
│   ├── task.py             # 태스크 관리 로직
│   └── comment.py          # 댓글 관리 로직
│
├── tests/                  # 테스트
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_projects.py
│   └── test_tasks.py
│
└── main.py                 # FastAPI 앱 엔트리포인트
```

### 비동기 처리

FastAPI와 SQLAlchemy 2.0의 비동기 기능을 활용합니다.

```python
# 모든 데이터베이스 작업은 async/await 사용
async def get_task_by_id(
    db: AsyncSession,
    task_id: int,
    project_id: int
) -> Task | None:
    result = await db.execute(
        select(Task)
        .where(Task.id == task_id, Task.project_id == project_id)
    )
    return result.scalar_one_or_none()
```

**장점**
- 높은 동시성 처리
- I/O 대기 시간 최소화
- 적은 리소스로 많은 요청 처리

### 의존성 주입 (Dependency Injection)

FastAPI의 `Depends`를 이용한 의존성 주입:

```python
# app/core/dependencies.py
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """데이터베이스 세션 제공"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """JWT 토큰에서 현재 사용자 추출"""
    # 토큰 검증 및 사용자 조회
    # ...
```

**장점**
- 코드 재사용성 증가
- 테스트 용이성 (Mock 주입 가능)
- 관심사 분리

---

## 프론트엔드 아키텍처

### Next.js 15 App Router

TaskFlow는 Next.js 15의 App Router를 사용하여 파일 시스템 기반 라우팅을 구현합니다.

```
frontend/app/
├── page.tsx                # 홈페이지 (/)
├── layout.tsx              # 전역 레이아웃
├── login/
│   └── page.tsx            # 로그인 (/login)
├── register/
│   └── page.tsx            # 회원가입 (/register)
├── dashboard/
│   └── page.tsx            # 대시보드 (/dashboard)
└── projects/
    ├── page.tsx            # 프로젝트 목록 (/projects)
    └── [id]/
        └── page.tsx        # 칸반 보드 (/projects/123)
```

### Server Components vs Client Components

#### Server Components (기본값)

```typescript
// app/projects/page.tsx
// 'use client' 없음 → 서버에서 렌더링

export default async function ProjectList() {
  // 서버에서 데이터 fetching
  const projects = await fetch('...');

  return (
    <div>
      {projects.map(p => <ProjectCard key={p.id} project={p} />)}
    </div>
  );
}
```

**특징**
- 서버에서 렌더링 (SEO 유리)
- 초기 로딩 속과
- 번들 크기 감소
- useState, useEffect 등 사용 불가

#### Client Components

```typescript
// components/kanban/KanbanBoard.tsx
'use client';  // 클라이언트 컴포넌트 명시

import { useState, useEffect } from 'react';

export default function KanbanBoard({ projectId }: Props) {
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    fetchTasks();
  }, [projectId]);

  // 드래그 앤 드롭 이벤트 핸들러
  const handleDrop = (taskId, newStatus) => {
    // ...
  };

  return <div>{/* ... */}</div>;
}
```

**특징**
- 클라이언트에서 렌더링
- React Hooks 사용 가능
- 인터랙티브 기능 (클릭, 드래그 등)

### 상태 관리

#### 1. React Context (AuthContext)

전역 인증 상태 관리:

```typescript
// contexts/AuthContext.tsx
'use client';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  const login = async (email: string, password: string) => {
    const response = await authApi.login({ email, password });
    setUser(response.user);
    setToken(response.token.access_token);
    setApiToken(response.token.access_token);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    setApiToken(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
```

#### 2. Local State (useState)

컴포넌트 내부 상태:

```typescript
const [tasks, setTasks] = useState<Task[]>([]);
const [isLoading, setIsLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
```

### API 클라이언트

타입 안전한 API 클라이언트:

```typescript
// lib/api.ts
export const taskApi = {
  create(projectId: number, data: TaskCreate): Promise<Task> {
    return api.post(`/api/v1/projects/${projectId}/tasks`, data);
  },

  list(projectId: number, params?: TaskListParams): Promise<Task[]> {
    return api.get(`/api/v1/projects/${projectId}/tasks`, params);
  },

  updateStatus(projectId: number, taskId: number, data: TaskStatusUpdate): Promise<Task> {
    return api.patch(`/api/v1/projects/${projectId}/tasks/${taskId}/status`, data);
  },
};
```

---

## 데이터베이스 스키마

### ERD (Entity Relationship Diagram)

```
┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│    User     │       │   Project    │       │    Task     │
├─────────────┤       ├──────────────┤       ├─────────────┤
│ id          │◄──┐   │ id           │◄──┐   │ id          │
│ email       │   │   │ name         │   │   │ title       │
│ hashed_pw   │   │   │ description  │   │   │ description │
│ name        │   │   │ owner_id ────┼───┘   │ status      │
│ created_at  │   │   │ created_at   │       │ priority    │
└─────────────┘   │   └──────────────┘       │ project_id ─┼───┐
                  │                           │ assignee_id ┼───┤
                  │                           │ created_at  │   │
                  │                           │ updated_at  │   │
                  │                           └─────────────┘   │
                  │                                              │
                  │   ┌──────────────┐                          │
                  └───┤ProjectMember │                          │
                      ├──────────────┤                          │
                      │ id           │                          │
                      │ user_id      │                          │
                      │ project_id   │                          │
                      │ role         │       ┌─────────────┐   │
                      └──────────────┘       │   Comment   │   │
                                             ├─────────────┤   │
                                             │ id          │   │
                                             │ content     │   │
                                             │ task_id ────┼───┘
                                             │ author_id   │
                                             │ created_at  │
                                             └─────────────┘
```

### 테이블 상세

#### Users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_users_email ON users(email);
```

#### Projects
```sql
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description VARCHAR(2000) DEFAULT '',
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Project Members
```sql
CREATE TABLE project_members (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member',
    UNIQUE(user_id, project_id)
);
```

#### Tasks
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    description VARCHAR(5000) DEFAULT '',
    status VARCHAR(50) DEFAULT 'todo',
    priority VARCHAR(50) DEFAULT 'medium',
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    assignee_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_status ON tasks(status);
```

#### Comments
```sql
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_comments_task_id ON comments(task_id);
```

### 관계 (Relationships)

- **User → Project**: 1:N (소유)
- **User ← → Project**: N:M (멤버십, ProjectMember 중간 테이블)
- **Project → Task**: 1:N
- **User → Task**: 1:N (담당자 배정)
- **Task → Comment**: 1:N
- **User → Comment**: 1:N (작성자)

### CASCADE 삭제 전략

- **프로젝트 삭제** → 관련 태스크, 댓글, 멤버십 모두 삭제
- **태스크 삭제** → 관련 댓글 모두 삭제
- **사용자 삭제** → 소유 프로젝트, 멤버십, 댓글 삭제
- **태스크 담당자 삭제** → `assignee_id`를 NULL로 설정 (SET NULL)

---

## API 설계 철학

### RESTful 원칙

TaskFlow API는 RESTful 설계 원칙을 따릅니다.

| HTTP Method | 용도 | 멱등성 | 예시 |
|-------------|------|--------|------|
| GET | 조회 | O | `GET /api/v1/tasks` |
| POST | 생성 | X | `POST /api/v1/tasks` |
| PUT | 전체 수정 | O | `PUT /api/v1/tasks/1` |
| PATCH | 부분 수정 | O | `PATCH /api/v1/tasks/1/status` |
| DELETE | 삭제 | O | `DELETE /api/v1/tasks/1` |

### 리소스 중첩

프로젝트 내의 태스크는 중첩된 라우트를 사용합니다.

```
POST   /api/v1/projects/{project_id}/tasks
GET    /api/v1/projects/{project_id}/tasks
GET    /api/v1/projects/{project_id}/tasks/{task_id}
PUT    /api/v1/projects/{project_id}/tasks/{task_id}
DELETE /api/v1/projects/{project_id}/tasks/{task_id}
```

**장점**
- 명확한 리소스 소유 관계
- 권한 검증 용이 (프로젝트 멤버만 접근)

### 응답 형식

#### 성공 응답

```json
{
  "id": 1,
  "title": "API 설계",
  "status": "in_progress",
  "created_at": "2024-01-15T12:00:00Z"
}
```

#### 에러 응답

```json
{
  "detail": "태스크를 찾을 수 없습니다."
}
```

#### 페이지네이션 (추후 구현 예정)

```json
{
  "data": [...],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

---

## 인증 및 인가

### JWT (JSON Web Token)

#### 로그인 플로우

```
1. Client: POST /api/v1/auth/login
   Body: { "email": "user@example.com", "password": "..." }

2. Server: 이메일/비밀번호 검증 (bcrypt)

3. Server: JWT 토큰 생성
   Payload: { "sub": "1", "exp": 1234567890 }
   Secret: JWT_SECRET_KEY

4. Server: Response
   { "user": {...}, "token": {"access_token": "eyJ..."} }

5. Client: 로컬스토리지에 토큰 저장
   localStorage.setItem('access_token', token)

6. Client: 이후 모든 요청에 토큰 포함
   Authorization: Bearer eyJ...
```

#### 토큰 검증

```python
# app/core/dependencies.py
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    # 1. 토큰 디코딩 및 검증
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    # 2. 사용자 ID 추출
    user_id = int(payload.get("sub"))

    # 3. 데이터베이스에서 사용자 조회
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
```

### 권한 관리 (RBAC)

프로젝트 단위의 역할 기반 접근 제어:

| 역할 | 권한 |
|------|------|
| **owner** | 모든 권한 (프로젝트 삭제 포함) |
| **admin** | 프로젝트 수정, 멤버 추가, 태스크 관리 |
| **member** | 태스크 조회, 생성, 수정 (삭제 불가) |

#### 프로젝트 멤버 검증

```python
# app/core/dependencies.py
async def get_project_member(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectMember:
    """현재 사용자가 프로젝트 멤버인지 확인"""
    result = await db.execute(
        select(ProjectMember)
        .where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=403,
            detail="프로젝트 멤버가 아닙니다."
        )

    return member
```

### 비밀번호 보안

- **해싱 알고리즘**: bcrypt
- **Salt**: 자동 생성 (bcrypt.gensalt())
- **검증**: 해시 비교 (bcrypt.checkpw())

```python
# app/core/security.py
def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)
```

---

## 드래그 앤 드롭 구현

### HTML5 Drag and Drop API

칸반 보드의 드래그 앤 드롭은 HTML5 API를 사용합니다.

```typescript
// components/kanban/KanbanBoard.tsx
const handleDragStart = (e: React.DragEvent, taskId: number) => {
  setDraggedTaskId(taskId);
  e.dataTransfer.effectAllowed = 'move';
};

const handleDragOver = (e: React.DragEvent) => {
  e.preventDefault();  // 드롭 허용
  e.dataTransfer.dropEffect = 'move';
};

const handleDrop = async (e: React.DragEvent, newStatus: TaskStatus) => {
  e.preventDefault();

  if (!draggedTaskId) return;

  // 1. 낙관적 업데이트 (즉시 UI 변경)
  const previousTasks = [...tasks];
  setTasks((prev) =>
    prev.map((t) =>
      t.id === draggedTaskId ? { ...t, status: newStatus } : t
    )
  );

  try {
    // 2. 서버에 상태 변경 요청
    await taskApi.updateStatus(projectId, draggedTaskId, { status: newStatus });
  } catch (err) {
    // 3. 실패 시 롤백
    console.error('Failed to update task status:', err);
    setTasks(previousTasks);
    alert('태스크 상태 변경에 실패했습니다.');
  } finally {
    setDraggedTaskId(null);
  }
};
```

### 낙관적 업데이트 (Optimistic Update)

**개념**: 서버 응답을 기다리지 않고 즉시 UI를 업데이트하여 사용자 경험을 개선합니다.

**플로우**
1. 사용자가 태스크를 드래그 앤 드롭
2. 즉시 UI 업데이트 (상태 변경)
3. 백엔드에 비동기 요청
4. 성공 시: UI 유지
5. 실패 시: 이전 상태로 롤백

**장점**
- 빠른 UI 반응
- 네트워크 지연 시에도 부드러운 UX

**단점**
- 에러 처리 복잡성 증가
- 충돌 가능성 (다른 사용자가 동시 수정)

---

## 기술 결정사항

### 1. FastAPI 선택 이유

**장점**
- 높은 성능 (Starlette 기반)
- 자동 API 문서 생성 (Swagger UI, ReDoc)
- Type Hints 기반 자동 유효성 검증 (Pydantic)
- 비동기 지원 (async/await)
- 현대적인 Python 기능 활용

**대안**: Django REST Framework, Flask
- FastAPI가 더 빠르고 타입 안전성이 높음

### 2. SQLAlchemy 2.0 선택 이유

**장점**
- ORM과 Raw SQL의 균형
- 비동기 지원 (asyncpg)
- 타입 힌트 지원 (Mapped, mapped_column)
- 강력한 관계 매핑

**대안**: Django ORM, Raw SQL
- 타입 안전성과 유연성 측면에서 SQLAlchemy 우위

### 3. Next.js 15 App Router 선택 이유

**장점**
- Server Components로 성능 최적화
- 파일 시스템 기반 라우팅 (간편함)
- 자동 코드 스플리팅
- SEO 최적화 (SSR, SSG)
- TypeScript 기본 지원

**대안**: React (CRA), Vue.js, Svelte
- Next.js가 프로덕션 준비 기능을 가장 많이 제공

### 4. JWT 인증 선택 이유

**장점**
- Stateless (서버에 세션 저장 불필요)
- 확장성 (수평 확장 용이)
- 모바일 앱 지원 용이

**대안**: Session 기반 인증
- JWT가 MSA 및 확장성에 유리

### 5. PostgreSQL 선택 이유

**장점**
- ACID 트랜잭션 지원
- 관계형 데이터 모델에 적합
- JSON 타입 지원 (향후 확장 가능)
- 무료 오픈소스

**대안**: MySQL, MongoDB
- PostgreSQL이 복잡한 쿼리와 트랜잭션에 강점

---

## 보안 고려사항

### 1. SQL Injection 방어

**방법**: SQLAlchemy의 파라미터화된 쿼리 사용

```python
# 안전 (파라미터화)
result = await db.execute(
    select(User).where(User.email == email)
)

# 위험 (Raw SQL with string concatenation)
# query = f"SELECT * FROM users WHERE email = '{email}'"  # ❌
```

### 2. XSS (Cross-Site Scripting) 방어

**방법**
- 프론트엔드: React의 자동 이스케이프
- 백엔드: Pydantic의 입력 검증

```typescript
// React는 자동으로 이스케이프
<div>{task.title}</div>  // 안전

// dangerouslySetInnerHTML는 사용 금지
<div dangerouslySetInnerHTML={{ __html: task.title }} />  // ❌
```

### 3. CSRF (Cross-Site Request Forgery) 방어

**방법**: SameSite 쿠키 설정 (추후 구현)

```python
# 쿠키 기반 인증 시
response.set_cookie(
    key="access_token",
    value=token,
    httponly=True,
    secure=True,
    samesite="lax"
)
```

### 4. CORS 설정

```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # 환경변수로 관리
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5. Rate Limiting (추후 구현)

slowapi를 이용한 속도 제한:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/auth/login")
@limiter.limit("5/minute")
async def login(...):
    pass
```

---

## 확장성 고려사항

### 수평 확장

#### 백엔드 확장

```yaml
# docker-compose.prod.yml
backend:
  image: taskflow-backend
  deploy:
    replicas: 3  # 3개의 인스턴스
  ports:
    - "8000-8002:8000"
```

Nginx 로드 밸런싱:

```nginx
upstream backend {
    server backend-1:8000;
    server backend-2:8000;
    server backend-3:8000;
}
```

#### 데이터베이스 Read Replica

```python
# app/core/database.py
read_engine = create_async_engine(READ_DATABASE_URL)
write_engine = create_async_engine(WRITE_DATABASE_URL)

# 읽기 전용 쿼리
async def get_tasks_readonly(db: AsyncSession):
    # read_engine 사용
    pass

# 쓰기 쿼리
async def create_task(db: AsyncSession):
    # write_engine 사용
    pass
```

### 캐싱 전략 (추후 구현)

#### Redis 캐싱

```python
import redis.asyncio as redis

# 프로젝트 목록 캐싱
@cache(expire=300)  # 5분 캐시
async def get_user_projects(db: AsyncSession, user_id: int):
    # ...
```

### 메시지 큐 (추후 구현)

이메일 알림, 백그라운드 작업 처리:

```python
# Celery + Redis
@celery.task
def send_notification_email(user_id: int, message: str):
    # 비동기 이메일 발송
    pass
```

---

## 추가 개선 사항

### 현재 구현되지 않은 기능

1. **실시간 업데이트** (WebSocket)
   - 다른 사용자의 변경사항 실시간 반영
   - Socket.IO 또는 FastAPI WebSocket 사용

2. **파일 첨부**
   - 태스크에 파일 업로드
   - S3 또는 MinIO 사용

3. **알림 시스템**
   - 태스크 배정, 댓글 작성 시 알림
   - 이메일 또는 푸시 알림

4. **검색 기능**
   - 태스크 전체 텍스트 검색
   - Elasticsearch 통합

5. **활동 로그**
   - 프로젝트 내 모든 활동 기록
   - Audit Trail

---

## 참고 자료

- **FastAPI 공식 문서**: https://fastapi.tiangolo.com/
- **SQLAlchemy 2.0 문서**: https://docs.sqlalchemy.org/en/20/
- **Next.js 15 문서**: https://nextjs.org/docs
- **PostgreSQL 문서**: https://www.postgresql.org/docs/

# TaskFlow - 팀 태스크 관리 웹앱

## 프로젝트 개요

TaskFlow는 팀 협업을 위한 태스크 관리 웹 애플리케이션입니다. 사용자 인증, 프로젝트 관리, 칸반 보드 기반의 태스크 관리, 담당자 배정, 댓글 기능을 제공합니다.

## 기술 스택

### 백엔드
- **Python 3.12**
- **FastAPI** - 웹 프레임워크
- **SQLAlchemy 2.0** - ORM
- **Alembic** - 데이터베이스 마이그레이션
- **JWT** - 인증/인가
- **PostgreSQL 16** - 데이터베이스

### 프론트엔드
- **Next.js 15 (App Router)** - React 프레임워크
- **TypeScript** - 타입 안정성
- **Tailwind CSS** - 스타일링

### 인프라
- **Docker** - 컨테이너화
- **Docker Compose** - 로컬 개발 환경

## 주요 기능

- 사용자 인증 및 권한 관리 (JWT)
- 프로젝트 생성 및 관리
- 태스크 CRUD (칸반 보드 UI)
- 담당자 배정
- 댓글 시스템
- 대시보드 (통계 및 현황)

## 코딩 컨벤션

### 백엔드 (Python/FastAPI)

- **PEP 8** 스타일 가이드 준수
- **Type hints 필수**: 모든 함수 매개변수와 반환값에 타입 힌트 사용
- **async/await 패턴**: 비동기 처리가 필요한 모든 I/O 작업에 사용
- 함수명과 변수명은 `snake_case` 사용
- 클래스명은 `PascalCase` 사용
- 상수는 `UPPER_SNAKE_CASE` 사용

예시:
```python
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_task_by_id(
    task_id: int,
    db: AsyncSession = Depends(get_db)
) -> Optional[Task]:
    """태스크 ID로 태스크 조회"""
    result = await db.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()
```

### 프론트엔드 (Next.js/TypeScript)

- **ESLint + Prettier** 설정 준수
- **함수형 컴포넌트** 사용
- **Server Components 우선**: 클라이언트 상태가 필요한 경우에만 `'use client'` 사용
- 컴포넌트명, 타입, 인터페이스는 `PascalCase`
- 함수명과 변수명은 `camelCase`
- 상수는 `UPPER_SNAKE_CASE`
- Props는 명시적 인터페이스로 정의

예시:
```typescript
interface TaskCardProps {
  taskId: number;
  title: string;
  assignee?: string;
}

export default async function TaskCard({
  taskId,
  title,
  assignee
}: TaskCardProps) {
  const task = await fetchTask(taskId);

  return (
    <div className="rounded-lg border p-4">
      <h3 className="text-lg font-semibold">{title}</h3>
      {assignee && <p className="text-sm text-gray-600">{assignee}</p>}
    </div>
  );
}
```

### Git 워크플로우

- **Conventional Commits** 형식 사용:
  - `feat:` - 새로운 기능
  - `fix:` - 버그 수정
  - `refactor:` - 코드 리팩토링
  - `docs:` - 문서 수정
  - `test:` - 테스트 추가/수정
  - `chore:` - 빌드, 설정 파일 수정

커밋 메시지 예시:
```
feat: 칸반 보드에 드래그 앤 드롭 기능 추가
fix: 태스크 삭제 시 댓글이 함께 삭제되지 않는 버그 수정
refactor: 사용자 인증 로직을 미들웨어로 분리
```

- **변경 전 반드시 새로운 branch 생성**:
```bash
git checkout -b feat/kanban-drag-drop
git checkout -b fix/task-deletion-bug
```

### API 개발

- **모든 API 엔드포인트는 테스트와 함께 작성**
- pytest와 FastAPI TestClient 사용
- 각 엔드포인트에 대해 정상 케이스와 에러 케이스 모두 테스트
- API 문서화는 FastAPI의 자동 문서 생성 활용 (docstring 작성)

테스트 예시:
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_task():
    """태스크 생성 API 테스트"""
    response = client.post(
        "/api/tasks",
        json={"title": "새 태스크", "project_id": 1}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "새 태스크"

def test_create_task_unauthorized():
    """인증 없이 태스크 생성 시도 테스트"""
    response = client.post(
        "/api/tasks",
        json={"title": "새 태스크", "project_id": 1}
    )
    assert response.status_code == 401
```

## 프로젝트 구조

```
taskflow/
├── backend/
│   ├── app/
│   │   ├── api/           # API 라우터
│   │   ├── core/          # 설정, 보안, 의존성
│   │   ├── models/        # SQLAlchemy 모델
│   │   ├── schemas/       # Pydantic 스키마
│   │   ├── services/      # 비즈니스 로직
│   │   └── tests/         # 테스트
│   ├── alembic/           # 마이그레이션
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/               # Next.js App Router
│   ├── components/        # React 컴포넌트
│   ├── lib/               # 유틸리티, API 클라이언트
│   ├── types/             # TypeScript 타입 정의
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── CLAUDE.md
```

## 개발 가이드라인

### 새로운 기능 개발 시

1. **브랜치 생성**: `git checkout -b feat/기능명`
2. **백엔드 작업**:
   - 모델 정의 (models/)
   - 스키마 정의 (schemas/)
   - 비즈니스 로직 구현 (services/)
   - API 엔드포인트 생성 (api/)
   - 테스트 작성 (tests/)
3. **마이그레이션**: DB 변경 시 `alembic revision --autogenerate`
4. **프론트엔드 작업**:
   - 타입 정의 (types/)
   - API 클라이언트 함수 (lib/)
   - 컴포넌트 구현 (components/)
   - 페이지/라우트 추가 (app/)
5. **테스트 실행 및 확인**
6. **커밋 및 푸시**: Conventional Commits 형식 준수

### 보안 고려사항

- JWT 토큰은 환경변수로 관리
- 비밀번호는 반드시 해싱하여 저장
- SQL Injection 방어: SQLAlchemy의 파라미터화된 쿼리 사용
- XSS 방어: 사용자 입력 sanitization
- CORS 설정 확인

### 성능 최적화

- 데이터베이스 쿼리 최적화 (N+1 문제 방지)
- 적절한 인덱스 사용
- Next.js의 Server Components와 Client Components 적절히 분리
- 이미지 최적화 (next/image 사용)

## 참고

- 모든 코드는 검토 없이 main 브랜치에 직접 푸시하지 않기
- 큰 기능은 여러 커밋으로 나누어 작업
- 의문점이 있으면 팀에 문의하거나 이슈 생성

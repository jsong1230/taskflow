# TaskFlow 프로젝트 초기 스캐폴딩 계획

**상태**: 완료
**작성일**: 2026-02-11

## Context

CLAUDE.md에 정의된 프로젝트 구조를 기반으로 실제 동작하는 초기 스캐폴딩을 구축합니다. 현재 프로젝트 루트에는 `CLAUDE.md`와 `.claude/agents/`만 존재하며, 백엔드/프론트엔드/인프라 전체 구조를 생성해야 합니다.

---

## 단계 1: 루트 인프라 파일 (5개)

| 파일 | 설명 |
|------|------|
| `.gitignore` | Python, Node.js, IDE, 환경변수, OS 파일 무시 |
| `.env.example` | 전체 환경변수 예시 (DB, JWT, CORS, Redis) |
| `docker-compose.yml` | PostgreSQL 16, Redis 7, 백엔드, 프론트엔드 서비스 |
| `backend/.dockerignore` | 백엔드 Docker 빌드 제외 파일 |
| `frontend/.dockerignore` | 프론트엔드 Docker 빌드 제외 파일 |

---

## 단계 2: 백엔드 (약 22개 파일)

### 핵심 파일 (의존성 순서대로)

1. **`backend/requirements.txt`** - FastAPI, SQLAlchemy 2.0, asyncpg, Alembic, python-jose, passlib, pydantic-settings, pytest, httpx
2. **`backend/app/__init__.py`** - 패키지 마커
3. **`backend/app/core/config.py`** - `pydantic-settings` BaseSettings로 환경변수 관리
4. **`backend/app/core/database.py`** - SQLAlchemy async 엔진, async_sessionmaker, DeclarativeBase
5. **`backend/app/core/security.py`** - JWT 토큰 생성/검증, bcrypt 비밀번호 해싱 (`datetime.now(timezone.utc)` 사용)
6. **`backend/app/core/dependencies.py`** - `get_db` (async generator), `get_current_user` (OAuth2 Bearer), `oauth2_scheme`
7. **`backend/app/models/__init__.py`** - Base import, 향후 모델 import 주석
8. **`backend/app/schemas/health.py`** - HealthResponse Pydantic 모델
9. **`backend/app/api/router.py`** - 통합 APIRouter, health 라우터 등록
10. **`backend/app/api/v1/health.py`** - `/health`, `/health/db` 엔드포인트
11. **`backend/app/main.py`** - FastAPI app (lifespan 패턴, CORS, 라우터 등록)

### Alembic 초기화

- `cd backend && python -m alembic init -t async alembic` 실행
- `alembic/env.py` 수정: `target_metadata = Base.metadata`, settings에서 DB URL 로드
- `alembic.ini` 수정: `sqlalchemy.url` 비움

### 테스트 & 기타

- **`backend/pytest.ini`** - asyncio_mode=auto, testpaths=app/tests
- **`backend/app/tests/conftest.py`** - httpx AsyncClient fixture
- **`backend/app/tests/test_health.py`** - health 엔드포인트 테스트
- **`backend/Dockerfile`** - 프로덕션 (비root 사용자, healthcheck)
- **`backend/Dockerfile.dev`** - 개발 (`--reload`)
- **`backend/.env.example`** - 백엔드 환경변수 예시
- 빈 `__init__.py` 파일들: `core/`, `api/`, `api/v1/`, `schemas/`, `services/`, `tests/`

---

## 단계 3: 프론트엔드 (create-next-app + 커스터마이징)

### Next.js 프로젝트 생성

```bash
npx create-next-app@latest frontend \
  --typescript --tailwind --eslint --app \
  --turbopack --no-src-dir --import-alias "@/*"
```

### 생성 후 커스터마이징

| 파일 | 작업 |
|------|------|
| `app/layout.tsx` | TaskFlow 제목, `lang="ko"`, Inter 폰트 |
| `app/page.tsx` | 심플한 TaskFlow 랜딩 페이지 |
| `next.config.ts` | `output: "standalone"` 추가 |
| `.eslintrc.json` | `"prettier"` extends 추가 |

### 새로 생성할 파일

| 파일 | 설명 |
|------|------|
| `types/index.ts` | User, Project, Task 타입 정의 |
| `lib/api-client.ts` | ApiError 클래스 + fetch 래퍼 함수 |
| `components/.gitkeep` | 디렉토리 구조 유지 |
| `.prettierrc.json` | Prettier 설정 (semi, singleQuote 등) |
| `Dockerfile` | 프로덕션 멀티스테이지 빌드 |
| `Dockerfile.dev` | 개발용 경량 이미지 |

### Prettier 설치

```bash
cd frontend && npm install --save-dev prettier eslint-config-prettier
```

---

## 단계 4: 검증

1. **백엔드 테스트**: `cd backend && pip install -r requirements.txt && pytest -v`
2. **프론트엔드 빌드**: `cd frontend && npm run build && npm run lint`
3. **Docker 통합** (선택): `docker compose up -d && curl localhost:8000/health`

---

## 핵심 설계 결정

- **프론트엔드**: `create-next-app` 사용 (직접 작성 대비 설정 안정성 높음)
- **SQLAlchemy**: 2.0 스타일 `DeclarativeBase` + `async_sessionmaker`
- **FastAPI lifespan**: `@asynccontextmanager` 패턴 (deprecated `on_event` 대신)
- **JWT datetime**: `datetime.now(timezone.utc)` (Python 3.12에서 `utcnow` deprecated)
- **get_db**: 자동 commit/rollback 패턴
- **Alembic**: `alembic init -t async`로 async 템플릿 사용

---

## 구현 결과

- 백엔드 health 테스트 통과 (1 passed)
- 프론트엔드 빌드 및 lint 통과
- 전체 프로젝트 구조 생성 완료
- Git 초기 커밋: "chore: initial project scaffolding with CLAUDE.md and agent definitions"

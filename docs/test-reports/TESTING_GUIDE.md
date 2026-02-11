# TaskFlow 테스트 가이드

이 문서는 TaskFlow 애플리케이션의 테스트 실행 방법과 테스트 작성 가이드라인을 제공합니다.

## 목차
1. [테스트 환경 설정](#테스트-환경-설정)
2. [테스트 실행](#테스트-실행)
3. [테스트 작성 가이드](#테스트-작성-가이드)
4. [CI/CD 통합](#cicd-통합)

---

## 테스트 환경 설정

### 1. Docker Compose 시작

```bash
# 프로젝트 루트에서 실행
docker-compose up -d

# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f backend
```

### 2. 로컬 개발 환경 (옵션)

```bash
cd backend

# 가상환경 생성
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일 편집하여 DATABASE_URL 등 설정
```

---

## 테스트 실행

### 전체 테스트 실행

```bash
cd backend
pytest app/tests/ -v
```

**출력 예시**:
```
============================= test session starts ==============================
collected 73 items

app/tests/test_auth.py::TestRegister::test_register_success PASSED       [  1%]
...
============================== 73 passed in 19.25s ==============================
```

### 특정 테스트 파일 실행

```bash
# 인증 테스트만
pytest app/tests/test_auth.py -v

# E2E 통합 테스트만
pytest app/tests/test_e2e_integration.py -v

# 프로젝트 테스트만
pytest app/tests/test_projects.py -v
```

### 특정 테스트 클래스 실행

```bash
# 회원가입 테스트만
pytest app/tests/test_auth.py::TestRegister -v

# 태스크 생성 테스트만
pytest app/tests/test_tasks.py::TestCreateTask -v
```

### 특정 테스트 메서드 실행

```bash
pytest app/tests/test_auth.py::TestRegister::test_register_success -v
```

### 키워드로 테스트 필터링

```bash
# "login"이 포함된 테스트만
pytest app/tests/ -k "login" -v

# "unauthorized"가 포함된 테스트만
pytest app/tests/ -k "unauthorized" -v
```

### 마커로 테스트 필터링

```bash
# asyncio 테스트만
pytest app/tests/ -m "asyncio" -v

# 느린 테스트 제외
pytest app/tests/ -m "not slow" -v
```

### 상세 출력 모드

```bash
# 매우 상세한 출력 (-vv)
pytest app/tests/ -vv

# 캡처된 출력 표시 (-s)
pytest app/tests/ -v -s

# 실패 시 즉시 중단 (-x)
pytest app/tests/ -v -x

# 처음 N개 실패 후 중단 (--maxfail=N)
pytest app/tests/ -v --maxfail=3
```

### 느린 테스트 확인

```bash
# 가장 느린 10개 테스트 표시
pytest app/tests/ --durations=10

# 가장 느린 20개 테스트 표시
pytest app/tests/ --durations=20
```

### 테스트 커버리지 측정

```bash
# 커버리지 측정 (pytest-cov 필요)
pip install pytest-cov

# 터미널 출력
pytest app/tests/ --cov=app --cov-report=term-missing

# HTML 리포트 생성
pytest app/tests/ --cov=app --cov-report=html

# 리포트 열기
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### 병렬 테스트 실행

```bash
# pytest-xdist 설치
pip install pytest-xdist

# 4개 워커로 병렬 실행
pytest app/tests/ -n 4

# CPU 코어 수만큼 워커 생성
pytest app/tests/ -n auto
```

### 테스트 결과 JSON 출력

```bash
# pytest-json-report 설치
pip install pytest-json-report

# JSON 리포트 생성
pytest app/tests/ --json-report --json-report-file=test_results.json
```

---

## 테스트 작성 가이드

### 기본 테스트 구조

```python
import pytest
from httpx import AsyncClient


class TestFeature:
    """기능 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_success_case(self, client: AsyncClient, auth_headers: dict):
        """정상 케이스 테스트"""
        response = await client.post(
            "/api/v1/endpoint",
            json={"key": "value"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["key"] == "value"

    @pytest.mark.asyncio
    async def test_error_case(self, client: AsyncClient):
        """에러 케이스 테스트"""
        response = await client.post(
            "/api/v1/endpoint",
            json={},  # 필수 필드 누락
        )

        assert response.status_code == 422
```

### 픽스처 사용

#### 사용 가능한 픽스처들 (conftest.py에서 정의)

```python
# 데이터베이스 세션
async def test_with_db(db_session: AsyncSession):
    pass

# 테스트 클라이언트
async def test_with_client(client: AsyncClient):
    pass

# 인증된 사용자
async def test_with_user(test_user: User, auth_headers: dict):
    pass

# 다른 사용자 (멤버십 없음)
async def test_with_other_user(other_user: User, other_auth_headers: dict):
    pass

# 테스트 프로젝트
async def test_with_project(test_project: Project):
    pass

# 테스트 태스크
async def test_with_task(test_task: Task):
    pass
```

### 테스트 작성 체크리스트

#### API 엔드포인트 테스트

- [ ] **정상 케이스** (200, 201, 204)
  ```python
  async def test_create_success(self, client, auth_headers):
      response = await client.post("/api/endpoint", json={...}, headers=auth_headers)
      assert response.status_code == 201
  ```

- [ ] **인증 없음** (401)
  ```python
  async def test_create_unauthorized(self, client):
      response = await client.post("/api/endpoint", json={...})
      assert response.status_code == 401
  ```

- [ ] **권한 없음** (403)
  ```python
  async def test_create_forbidden(self, client, other_auth_headers):
      response = await client.post("/api/endpoint", json={...}, headers=other_auth_headers)
      assert response.status_code == 403
  ```

- [ ] **리소스 없음** (404)
  ```python
  async def test_get_not_found(self, client, auth_headers):
      response = await client.get("/api/endpoint/99999", headers=auth_headers)
      assert response.status_code == 404
  ```

- [ ] **잘못된 입력** (422)
  ```python
  async def test_create_invalid_input(self, client, auth_headers):
      response = await client.post("/api/endpoint", json={}, headers=auth_headers)
      assert response.status_code == 422
  ```

### 비동기 테스트 작성

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_async_operation(client: AsyncClient):
    """비동기 작업 테스트"""
    # 여러 요청 동시 실행
    responses = await asyncio.gather(
        client.get("/api/endpoint1"),
        client.get("/api/endpoint2"),
        client.get("/api/endpoint3"),
    )

    for response in responses:
        assert response.status_code == 200
```

### 데이터베이스 테스트

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
async def test_database_operation(db_session: AsyncSession):
    """데이터베이스 작업 테스트"""
    # 데이터 생성
    user = User(email="test@example.com", name="Test")
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)

    # 데이터 조회
    result = await db_session.execute(
        select(User).where(User.email == "test@example.com")
    )
    found_user = result.scalar_one()

    assert found_user.id == user.id
```

### 모킹 (Mocking)

```python
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_with_mock(client: AsyncClient, auth_headers: dict):
    """외부 서비스 모킹"""
    with patch('app.services.external_service.call_api') as mock_api:
        mock_api.return_value = {"status": "success"}

        response = await client.post(
            "/api/endpoint",
            json={"data": "test"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        mock_api.assert_called_once()
```

### 파라미터화된 테스트

```python
import pytest


@pytest.mark.parametrize("email,password,expected_status", [
    ("valid@example.com", "password123", 201),
    ("invalid-email", "password123", 422),
    ("", "password123", 422),
    ("test@example.com", "", 422),
])
@pytest.mark.asyncio
async def test_register_various_inputs(
    client: AsyncClient,
    email: str,
    password: str,
    expected_status: int
):
    """다양한 입력값 테스트"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "name": "Test User",
        },
    )
    assert response.status_code == expected_status
```

---

## CI/CD 통합

### GitHub Actions 예시

`.github/workflows/test.yml` 생성:

```yaml
name: Tests

on:
  push:
    branches: [ master, main, develop ]
  pull_request:
    branches: [ master, main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: taskflow
          POSTGRES_PASSWORD: taskflow_secret
          POSTGRES_DB: taskflow_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run tests
      env:
        DATABASE_URL: postgresql+asyncpg://taskflow:taskflow_secret@localhost:5432/taskflow_test
        JWT_SECRET_KEY: test-secret-key
      run: |
        cd backend
        pytest app/tests/ -v --cov=app --cov-report=xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
```

### GitLab CI 예시

`.gitlab-ci.yml` 생성:

```yaml
stages:
  - test

variables:
  POSTGRES_DB: taskflow_test
  POSTGRES_USER: taskflow
  POSTGRES_PASSWORD: taskflow_secret

test:
  stage: test
  image: python:3.11
  services:
    - postgres:16-alpine
  variables:
    DATABASE_URL: postgresql+asyncpg://taskflow:taskflow_secret@postgres:5432/taskflow_test
    JWT_SECRET_KEY: test-secret-key
  before_script:
    - cd backend
    - pip install -r requirements.txt
    - pip install -r requirements-dev.txt
  script:
    - pytest app/tests/ -v --cov=app --cov-report=term
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

---

## 유용한 pytest 옵션

### 디버깅

```bash
# 첫 번째 실패에서 pdb 시작
pytest app/tests/ --pdb

# 모든 테스트에서 pdb 시작
pytest app/tests/ --trace

# 캡처 비활성화 (print 문 보기)
pytest app/tests/ -s
```

### 경고 제어

```bash
# 경고를 에러로 처리
pytest app/tests/ -W error

# 경고 무시
pytest app/tests/ -W ignore
```

### 출력 제어

```bash
# 간결한 출력
pytest app/tests/ -q

# 요약만
pytest app/tests/ --tb=no

# 짧은 traceback
pytest app/tests/ --tb=short

# 긴 traceback
pytest app/tests/ --tb=long
```

---

## 트러블슈팅

### 일반적인 문제와 해결 방법

#### 1. 데이터베이스 연결 실패

**문제**: `sqlalchemy.exc.OperationalError: could not connect to server`

**해결**:
```bash
# Docker Compose 서비스 확인
docker-compose ps

# PostgreSQL 로그 확인
docker-compose logs db

# 컨테이너 재시작
docker-compose restart db
```

#### 2. 픽스처 오류

**문제**: `fixture 'xxx' not found`

**해결**:
- `conftest.py` 파일이 올바른 위치에 있는지 확인
- 픽스처 이름 철자 확인
- 필요한 의존성 픽스처가 정의되어 있는지 확인

#### 3. 비동기 테스트 오류

**문제**: `RuntimeError: no running event loop`

**해결**:
```python
# @pytest.mark.asyncio 데코레이터 추가
@pytest.mark.asyncio
async def test_function():
    pass
```

#### 4. 테스트 격리 문제

**문제**: 테스트가 서로 영향을 미침

**해결**:
- `conftest.py`의 `db_session` 픽스처가 트랜잭션 롤백하는지 확인
- 각 테스트에서 독립적인 데이터 사용
- 테스트 순서에 의존하지 않기

---

## 베스트 프랙티스

1. **독립성**: 각 테스트는 독립적으로 실행 가능해야 함
2. **명확한 이름**: 테스트 이름에서 무엇을 테스트하는지 명확히
3. **AAA 패턴**: Arrange (준비), Act (실행), Assert (검증)
4. **하나의 개념**: 각 테스트는 하나의 개념만 테스트
5. **에러 메시지**: 의미 있는 assert 메시지 작성
6. **테스트 속도**: 빠른 테스트 유지 (모킹 활용)
7. **커버리지**: 80% 이상 목표
8. **문서화**: 복잡한 테스트는 docstring 추가

---

## 참고 자료

- [pytest 공식 문서](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [httpx AsyncClient](https://www.python-httpx.org/async/)

---

**작성일**: 2026-02-11
**작성자**: QA Engineer Agent
**버전**: 1.0

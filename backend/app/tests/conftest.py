import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.dependencies import get_db
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.project import Project, ProjectMember, ProjectRole
from app.models.task import Task
from app.models.user import User


@pytest_asyncio.fixture
async def db_session():
    """
    테스트용 DB 세션.
    각 테스트를 하나의 트랜잭션 안에서 실행하고 끝나면 롤백하여
    테스트 간 데이터 격리를 보장한다.
    """
    # 각 테스트마다 새 엔진 생성 (NullPool로 connection pool 충돌 방지)
    engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)

    conn = await engine.connect()
    txn = await conn.begin()
    session = AsyncSession(bind=conn, expire_on_commit=False)

    yield session

    await session.close()
    await txn.rollback()
    await conn.close()
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    """테스트용 클라이언트 (get_db를 테스트 세션으로 override)"""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """테스트용 사용자"""
    user = User(
        email="test@example.com",
        name="Test User",
        hashed_password=hash_password("test1234"),
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """인증 헤더"""
    access_token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


@pytest_asyncio.fixture
async def other_user(db_session: AsyncSession) -> User:
    """멤버십 없는 다른 사용자"""
    user = User(
        email="other@example.com",
        name="Other User",
        hashed_password=hash_password("other1234"),
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest.fixture
def other_auth_headers(other_user: User) -> dict:
    """other_user의 인증 헤더"""
    access_token = create_access_token(data={"sub": str(other_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


@pytest_asyncio.fixture
async def test_project(db_session: AsyncSession, test_user: User) -> Project:
    """test_user가 owner인 프로젝트 (멤버십 자동 추가)"""
    project = Project(
        name="Test Project",
        description="A test project",
        owner_id=test_user.id,
    )
    db_session.add(project)
    await db_session.flush()

    member = ProjectMember(
        user_id=test_user.id,
        project_id=project.id,
        role=ProjectRole.owner,
    )
    db_session.add(member)
    await db_session.flush()
    await db_session.refresh(project)
    return project


@pytest_asyncio.fixture
async def test_task(db_session: AsyncSession, test_project: Project) -> Task:
    """test_project에 속한 태스크"""
    task = Task(
        title="Test Task",
        description="A test task",
        project_id=test_project.id,
    )
    db_session.add(task)
    await db_session.flush()
    await db_session.refresh(task)
    return task

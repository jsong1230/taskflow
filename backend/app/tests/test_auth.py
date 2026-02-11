from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class TestRegister:
    """회원가입 테스트"""

    async def test_register_success(self, client: AsyncClient, db_session: AsyncSession):
        """정상적인 회원가입"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "pass1234",
                "name": "New User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["name"] == "New User"
        assert "id" in data
        assert "created_at" in data
        assert "hashed_password" not in data

        # DB에 사용자가 생성되었는지 확인
        result = await db_session.execute(select(User).where(User.email == "newuser@example.com"))
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.email == "newuser@example.com"
        assert user.name == "New User"
        # 비밀번호가 해싱되었는지 확인
        assert user.hashed_password != "pass1234"
        assert user.hashed_password.startswith("$2b$")

    async def test_register_duplicate_email(self, client: AsyncClient, test_user: User):
        """중복된 이메일로 회원가입 시도"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "password": "pass1234",
                "name": "Duplicate User",
            },
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "이미 등록된 이메일입니다."

    async def test_register_invalid_email(self, client: AsyncClient):
        """잘못된 이메일 형식"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "pass1234",
                "name": "Test User",
            },
        )
        assert response.status_code == 422

    async def test_register_missing_fields(self, client: AsyncClient):
        """필수 필드 누락"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
            },
        )
        assert response.status_code == 422


class TestLogin:
    """로그인 테스트"""

    async def test_login_success(self, client: AsyncClient, test_user: User):
        """정상적인 로그인"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "test1234",
            },
        )
        assert response.status_code == 200
        data = response.json()

        # 사용자 정보 확인
        assert "user" in data
        assert data["user"]["email"] == test_user.email
        assert data["user"]["name"] == test_user.name
        assert data["user"]["id"] == test_user.id

        # 토큰 확인
        assert "token" in data
        assert "access_token" in data["token"]
        assert data["token"]["token_type"] == "bearer"
        assert isinstance(data["token"]["access_token"], str)
        assert len(data["token"]["access_token"]) > 0

    async def test_login_wrong_password(self, client: AsyncClient, test_user: User):
        """잘못된 비밀번호"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "이메일 또는 비밀번호가 올바르지 않습니다."

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """존재하지 않는 사용자"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "pass1234",
            },
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "이메일 또는 비밀번호가 올바르지 않습니다."

    async def test_login_invalid_email(self, client: AsyncClient):
        """잘못된 이메일 형식"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "invalid-email",
                "password": "pass1234",
            },
        )
        assert response.status_code == 422

    async def test_login_missing_fields(self, client: AsyncClient):
        """필수 필드 누락"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
            },
        )
        assert response.status_code == 422


class TestGetMe:
    """현재 사용자 정보 조회 테스트"""

    async def test_get_me_success(self, client: AsyncClient, test_user: User, auth_headers: dict):
        """정상적인 현재 사용자 정보 조회"""
        response = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name
        assert data["id"] == test_user.id
        assert "created_at" in data
        assert "hashed_password" not in data

    async def test_get_me_no_token(self, client: AsyncClient):
        """토큰 없이 요청"""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    async def test_get_me_invalid_token(self, client: AsyncClient):
        """잘못된 토큰"""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "유효하지 않은 인증 정보입니다."

    async def test_get_me_malformed_token(self, client: AsyncClient):
        """형식이 잘못된 토큰"""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "InvalidFormat token"},
        )
        assert response.status_code == 401


class TestAuthIntegration:
    """인증 시스템 통합 테스트"""

    async def test_register_login_get_me_flow(self, client: AsyncClient):
        """회원가입 -> 로그인 -> 사용자 정보 조회 전체 플로우"""
        # 1. 회원가입
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "flowtest@example.com",
                "password": "flowpass1234",
                "name": "Flow Test User",
            },
        )
        assert register_response.status_code == 201
        user_data = register_response.json()

        # 2. 로그인
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "flowtest@example.com",
                "password": "flowpass1234",
            },
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        token = login_data["token"]["access_token"]

        # 3. 사용자 정보 조회
        me_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data["email"] == "flowtest@example.com"
        assert me_data["name"] == "Flow Test User"
        assert me_data["id"] == user_data["id"]

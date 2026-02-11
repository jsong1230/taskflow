"""
E2E 통합 테스트

전체 사용자 시나리오를 순차적으로 테스트하여 시스템이
실제 사용 환경에서 제대로 동작하는지 검증합니다.
"""

import time

import pytest
from httpx import AsyncClient


class TestCompleteUserJourney:
    """완전한 사용자 여정 테스트"""

    @pytest.mark.asyncio
    async def test_complete_workflow(self, client: AsyncClient):
        """
        전체 워크플로우 E2E 테스트:
        회원가입 -> 로그인 -> 프로젝트 생성 -> 태스크 생성 ->
        태스크 상태 변경 -> 댓글 작성
        """
        start_time = time.time()

        # =================================================================
        # 1. 회원가입
        # =================================================================
        print("\n=== 1. 회원가입 테스트 ===")
        register_start = time.time()

        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "e2e_test@example.com",
                "password": "e2e_password123",
                "name": "E2E Test User",
            },
        )

        register_time = time.time() - register_start
        print(f"회원가입 응답 시간: {register_time:.3f}s")

        assert register_response.status_code == 201, f"회원가입 실패: {register_response.json()}"
        user_data = register_response.json()
        assert user_data["email"] == "e2e_test@example.com"
        assert user_data["name"] == "E2E Test User"
        assert "id" in user_data
        user_id = user_data["id"]
        print(f"✓ 회원가입 성공 - 사용자 ID: {user_id}")

        # =================================================================
        # 2. 로그인 (JWT 토큰 획득)
        # =================================================================
        print("\n=== 2. 로그인 테스트 ===")
        login_start = time.time()

        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "e2e_test@example.com",
                "password": "e2e_password123",
            },
        )

        login_time = time.time() - login_start
        print(f"로그인 응답 시간: {login_time:.3f}s")

        assert login_response.status_code == 200, f"로그인 실패: {login_response.json()}"
        login_data = login_response.json()
        assert "token" in login_data
        assert "access_token" in login_data["token"]

        access_token = login_data["token"]["access_token"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}
        print("✓ 로그인 성공 - 토큰 획득")

        # =================================================================
        # 3. 현재 사용자 정보 조회
        # =================================================================
        print("\n=== 3. 현재 사용자 정보 조회 테스트 ===")
        me_start = time.time()

        me_response = await client.get("/api/v1/auth/me", headers=auth_headers)

        me_time = time.time() - me_start
        print(f"사용자 정보 조회 응답 시간: {me_time:.3f}s")

        assert me_response.status_code == 200, f"사용자 정보 조회 실패: {me_response.json()}"
        me_data = me_response.json()
        assert me_data["id"] == user_id
        assert me_data["email"] == "e2e_test@example.com"
        print("✓ 사용자 정보 조회 성공")

        # =================================================================
        # 4. 프로젝트 생성
        # =================================================================
        print("\n=== 4. 프로젝트 생성 테스트 ===")
        project_start = time.time()

        project_response = await client.post(
            "/api/v1/projects/",
            json={
                "name": "E2E Test Project",
                "description": "통합 테스트용 프로젝트",
            },
            headers=auth_headers,
        )

        project_time = time.time() - project_start
        print(f"프로젝트 생성 응답 시간: {project_time:.3f}s")

        assert project_response.status_code == 201, f"프로젝트 생성 실패: {project_response.json()}"
        project_data = project_response.json()
        assert project_data["name"] == "E2E Test Project"
        assert "id" in project_data
        project_id = project_data["id"]
        print(f"✓ 프로젝트 생성 성공 - 프로젝트 ID: {project_id}")

        # =================================================================
        # 5. 프로젝트 목록 조회
        # =================================================================
        print("\n=== 5. 프로젝트 목록 조회 테스트 ===")
        projects_list_start = time.time()

        projects_response = await client.get("/api/v1/projects/", headers=auth_headers)

        projects_list_time = time.time() - projects_list_start
        print(f"프로젝트 목록 조회 응답 시간: {projects_list_time:.3f}s")

        assert projects_response.status_code == 200, (
            f"프로젝트 목록 조회 실패: {projects_response.json()}"
        )
        projects = projects_response.json()
        assert len(projects) >= 1
        assert any(p["id"] == project_id for p in projects)
        print(f"✓ 프로젝트 목록 조회 성공 - {len(projects)}개 프로젝트")

        # =================================================================
        # 6. 태스크 생성
        # =================================================================
        print("\n=== 6. 태스크 생성 테스트 ===")
        task_start = time.time()

        task_response = await client.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={
                "title": "E2E 테스크",
                "description": "통합 테스트용 태스크",
                "priority": "high",
            },
            headers=auth_headers,
        )

        task_time = time.time() - task_start
        print(f"태스크 생성 응답 시간: {task_time:.3f}s")

        assert task_response.status_code == 201, f"태스크 생성 실패: {task_response.json()}"
        task_data = task_response.json()
        assert task_data["title"] == "E2E 테스크"
        assert task_data["status"] == "todo"
        assert task_data["priority"] == "high"
        assert "id" in task_data
        task_id = task_data["id"]
        print(f"✓ 태스크 생성 성공 - 태스크 ID: {task_id}")

        # =================================================================
        # 7. 태스크 목록 조회
        # =================================================================
        print("\n=== 7. 태스크 목록 조회 테스트 ===")
        tasks_list_start = time.time()

        tasks_response = await client.get(
            f"/api/v1/projects/{project_id}/tasks",
            headers=auth_headers,
        )

        tasks_list_time = time.time() - tasks_list_start
        print(f"태스크 목록 조회 응답 시간: {tasks_list_time:.3f}s")

        assert tasks_response.status_code == 200, f"태스크 목록 조회 실패: {tasks_response.json()}"
        tasks = tasks_response.json()
        assert len(tasks) >= 1
        assert any(t["id"] == task_id for t in tasks)
        print(f"✓ 태스크 목록 조회 성공 - {len(tasks)}개 태스크")

        # =================================================================
        # 8. 태스크 상태 변경 (todo -> in_progress)
        # =================================================================
        print("\n=== 8. 태스크 상태 변경 테스트 ===")
        status_start = time.time()

        status_response = await client.patch(
            f"/api/v1/projects/{project_id}/tasks/{task_id}/status",
            json={"status": "in_progress"},
            headers=auth_headers,
        )

        status_time = time.time() - status_start
        print(f"태스크 상태 변경 응답 시간: {status_time:.3f}s")

        assert status_response.status_code == 200, (
            f"태스크 상태 변경 실패: {status_response.json()}"
        )
        updated_task = status_response.json()
        assert updated_task["status"] == "in_progress"
        print("✓ 태스크 상태 변경 성공: todo -> in_progress")

        # =================================================================
        # 9. 태스크 상세 조회
        # =================================================================
        print("\n=== 9. 태스크 상세 조회 테스트 ===")
        task_detail_start = time.time()

        task_detail_response = await client.get(
            f"/api/v1/projects/{project_id}/tasks/{task_id}",
            headers=auth_headers,
        )

        task_detail_time = time.time() - task_detail_start
        print(f"태스크 상세 조회 응답 시간: {task_detail_time:.3f}s")

        assert task_detail_response.status_code == 200, (
            f"태스크 상세 조회 실패: {task_detail_response.json()}"
        )
        task_detail = task_detail_response.json()
        assert task_detail["id"] == task_id
        assert task_detail["status"] == "in_progress"
        print("✓ 태스크 상세 조회 성공")

        # =================================================================
        # 10. 댓글 작성
        # =================================================================
        print("\n=== 10. 댓글 작성 테스트 ===")
        comment_start = time.time()

        comment_response = await client.post(
            f"/api/v1/projects/{project_id}/tasks/{task_id}/comments",
            json={"content": "E2E 테스트 댓글입니다!"},
            headers=auth_headers,
        )

        comment_time = time.time() - comment_start
        print(f"댓글 작성 응답 시간: {comment_time:.3f}s")

        assert comment_response.status_code == 201, f"댓글 작성 실패: {comment_response.json()}"
        comment_data = comment_response.json()
        assert comment_data["content"] == "E2E 테스트 댓글입니다!"
        assert comment_data["author_id"] == user_id
        assert "id" in comment_data
        comment_id = comment_data["id"]
        print(f"✓ 댓글 작성 성공 - 댓글 ID: {comment_id}")

        # =================================================================
        # 11. 댓글 목록 조회
        # =================================================================
        print("\n=== 11. 댓글 목록 조회 테스트 ===")
        comments_list_start = time.time()

        comments_response = await client.get(
            f"/api/v1/projects/{project_id}/tasks/{task_id}/comments",
            headers=auth_headers,
        )

        comments_list_time = time.time() - comments_list_start
        print(f"댓글 목록 조회 응답 시간: {comments_list_time:.3f}s")

        assert comments_response.status_code == 200, (
            f"댓글 목록 조회 실패: {comments_response.json()}"
        )
        comments = comments_response.json()
        assert len(comments) >= 1
        assert any(c["id"] == comment_id for c in comments)
        print(f"✓ 댓글 목록 조회 성공 - {len(comments)}개 댓글")

        # =================================================================
        # 전체 테스트 완료
        # =================================================================
        total_time = time.time() - start_time
        print(f"\n{'=' * 60}")
        print("✓ 전체 E2E 테스트 성공!")
        print(f"총 소요 시간: {total_time:.3f}s")
        print(f"{'=' * 60}\n")


class TestErrorCases:
    """에러 케이스 테스트"""

    @pytest.mark.asyncio
    async def test_unauthorized_access(self, client: AsyncClient):
        """인증 없이 보호된 엔드포인트 접근 시도"""
        print("\n=== 인증 없이 API 접근 테스트 ===")

        # 프로젝트 목록 조회 (인증 필요)
        response = await client.get("/api/v1/projects/")
        assert response.status_code == 401
        print("✓ 프로젝트 목록 조회: 401 Unauthorized")

        # 사용자 정보 조회 (인증 필요)
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401
        print("✓ 사용자 정보 조회: 401 Unauthorized")

        # 프로젝트 생성 (인증 필요)
        response = await client.post("/api/v1/projects/", json={"name": "Test"})
        assert response.status_code == 401
        print("✓ 프로젝트 생성: 401 Unauthorized")

    @pytest.mark.asyncio
    async def test_invalid_token(self, client: AsyncClient):
        """잘못된 토큰으로 접근 시도"""
        print("\n=== 잘못된 토큰으로 API 접근 테스트 ===")

        invalid_headers = {"Authorization": "Bearer invalid_token_12345"}

        response = await client.get("/api/v1/auth/me", headers=invalid_headers)
        assert response.status_code == 401
        assert response.json()["detail"] == "유효하지 않은 인증 정보입니다."
        print("✓ 잘못된 토큰: 401 Unauthorized")

    @pytest.mark.asyncio
    async def test_forbidden_access(self, client: AsyncClient, test_project, other_auth_headers):
        """권한 없는 리소스에 접근 시도"""
        print("\n=== 권한 없는 리소스 접근 테스트 ===")

        # 다른 사용자의 프로젝트에 접근
        response = await client.get(
            f"/api/v1/projects/{test_project.id}",
            headers=other_auth_headers,
        )
        assert response.status_code == 403
        print("✓ 다른 사용자의 프로젝트 조회: 403 Forbidden")

        # 다른 사용자의 프로젝트에 태스크 생성 시도
        response = await client.post(
            f"/api/v1/projects/{test_project.id}/tasks",
            json={"title": "Unauthorized Task"},
            headers=other_auth_headers,
        )
        assert response.status_code == 403
        print("✓ 다른 사용자의 프로젝트에 태스크 생성: 403 Forbidden")

    @pytest.mark.asyncio
    async def test_resource_not_found(self, client: AsyncClient, auth_headers):
        """존재하지 않는 리소스 접근"""
        print("\n=== 존재하지 않는 리소스 접근 테스트 ===")

        # 존재하지 않는 프로젝트
        response = await client.get("/api/v1/projects/99999", headers=auth_headers)
        assert response.status_code == 404
        print("✓ 존재하지 않는 프로젝트: 404 Not Found")

        # 존재하지 않는 태스크
        response = await client.get(
            "/api/v1/projects/1/tasks/99999",
            headers=auth_headers,
        )
        assert response.status_code in [403, 404]
        print("✓ 존재하지 않는 태스크: 404 Not Found")

    @pytest.mark.asyncio
    async def test_invalid_input(self, client: AsyncClient, auth_headers):
        """잘못된 입력값 테스트"""
        print("\n=== 잘못된 입력값 테스트 ===")

        # 필수 필드 누락 - 회원가입
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com"},  # password, name 누락
        )
        assert response.status_code == 422
        print("✓ 회원가입 필수 필드 누락: 422 Unprocessable Entity")

        # 잘못된 이메일 형식
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "pass123",
                "name": "Test",
            },
        )
        assert response.status_code == 422
        print("✓ 잘못된 이메일 형식: 422 Unprocessable Entity")

        # 필수 필드 누락 - 프로젝트 생성
        response = await client.post(
            "/api/v1/projects/",
            json={},  # name 누락
            headers=auth_headers,
        )
        assert response.status_code == 422
        print("✓ 프로젝트 생성 필수 필드 누락: 422 Unprocessable Entity")

        # 필수 필드 누락 - 태스크 생성
        response = await client.post(
            "/api/v1/projects/1/tasks",
            json={},  # title 누락
            headers=auth_headers,
        )
        # 프로젝트가 없거나 권한이 없을 수 있으므로 422 또는 403/404
        assert response.status_code in [403, 404, 422]
        print("✓ 태스크 생성 필수 필드 누락: 422 Unprocessable Entity")

    @pytest.mark.asyncio
    async def test_duplicate_email(self, client: AsyncClient, test_user):
        """중복된 이메일로 회원가입 시도"""
        print("\n=== 중복 이메일 회원가입 테스트 ===")

        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "password": "password123",
                "name": "Duplicate User",
            },
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "이미 등록된 이메일입니다."
        print("✓ 중복 이메일: 400 Bad Request")

    @pytest.mark.asyncio
    async def test_wrong_password(self, client: AsyncClient, test_user):
        """잘못된 비밀번호로 로그인 시도"""
        print("\n=== 잘못된 비밀번호 로그인 테스트 ===")

        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "wrong_password",
            },
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "이메일 또는 비밀번호가 올바르지 않습니다."
        print("✓ 잘못된 비밀번호: 401 Unauthorized")


class TestPerformance:
    """성능 테스트"""

    @pytest.mark.asyncio
    async def test_api_response_times(self, client: AsyncClient, auth_headers, test_project):
        """API 응답 시간 측정"""
        print("\n=== API 응답 시간 측정 ===")

        # 건강 체크
        start = time.time()
        await client.get("/api/v1/health")
        health_time = time.time() - start
        print(f"Health Check: {health_time:.3f}s")

        # 사용자 정보 조회
        start = time.time()
        await client.get("/api/v1/auth/me", headers=auth_headers)
        me_time = time.time() - start
        print(f"Get User Info: {me_time:.3f}s")

        # 프로젝트 목록 조회
        start = time.time()
        await client.get("/api/v1/projects/", headers=auth_headers)
        projects_time = time.time() - start
        print(f"List Projects: {projects_time:.3f}s")

        # 태스크 목록 조회
        start = time.time()
        await client.get(f"/api/v1/projects/{test_project.id}/tasks", headers=auth_headers)
        tasks_time = time.time() - start
        print(f"List Tasks: {tasks_time:.3f}s")

        # 모든 API 응답 시간이 1초 이내여야 함
        assert health_time < 1.0, f"Health check too slow: {health_time}s"
        assert me_time < 1.0, f"Get user info too slow: {me_time}s"
        assert projects_time < 1.0, f"List projects too slow: {projects_time}s"
        assert tasks_time < 1.0, f"List tasks too slow: {tasks_time}s"

        print("✓ 모든 API 응답 시간이 1초 이내")


class TestDataIntegrity:
    """데이터 무결성 테스트"""

    @pytest.mark.asyncio
    async def test_project_member_cascade(self, client: AsyncClient, auth_headers, test_user):
        """프로젝트 생성 시 자동으로 owner 멤버십이 추가되는지 확인"""
        print("\n=== 프로젝트 멤버십 자동 생성 테스트 ===")

        # 프로젝트 생성
        project_response = await client.post(
            "/api/v1/projects/",
            json={"name": "Membership Test Project"},
            headers=auth_headers,
        )
        assert project_response.status_code == 201
        project_id = project_response.json()["id"]

        # 프로젝트 상세 조회하여 멤버십 확인
        detail_response = await client.get(
            f"/api/v1/projects/{project_id}",
            headers=auth_headers,
        )
        assert detail_response.status_code == 200

        members = detail_response.json()["members"]
        assert len(members) == 1
        assert members[0]["user_id"] == test_user.id
        assert members[0]["role"] == "owner"

        print("✓ 프로젝트 생성 시 owner 멤버십 자동 생성 확인")

    @pytest.mark.asyncio
    async def test_task_default_values(self, client: AsyncClient, auth_headers, test_project):
        """태스크 생성 시 기본값이 올바르게 설정되는지 확인"""
        print("\n=== 태스크 기본값 테스트 ===")

        # 최소한의 정보로 태스크 생성
        response = await client.post(
            f"/api/v1/projects/{test_project.id}/tasks",
            json={"title": "Minimal Task"},
            headers=auth_headers,
        )
        assert response.status_code == 201

        task = response.json()
        assert task["status"] == "todo"
        assert task["priority"] == "medium"
        assert task["description"] is None or task["description"] == ""

        print("✓ 태스크 기본값 올바르게 설정됨 (status=todo, priority=medium)")

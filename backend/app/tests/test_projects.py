import pytest
from httpx import AsyncClient


BASE = "/api/v1/projects"


class TestCreateProject:
    @pytest.mark.asyncio
    async def test_create_project_success(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            BASE + "/",
            json={"name": "My Project", "description": "desc"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Project"
        assert data["description"] == "desc"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_project_owner_membership(
        self, client: AsyncClient, auth_headers: dict
    ):
        """생성 후 owner 멤버십이 자동 추가되는지 확인"""
        resp = await client.post(
            BASE + "/",
            json={"name": "PM Test"},
            headers=auth_headers,
        )
        project_id = resp.json()["id"]

        detail = await client.get(f"{BASE}/{project_id}", headers=auth_headers)
        assert detail.status_code == 200
        members = detail.json()["members"]
        assert len(members) == 1
        assert members[0]["role"] == "owner"

    @pytest.mark.asyncio
    async def test_create_project_unauthorized(self, client: AsyncClient):
        response = await client.post(BASE + "/", json={"name": "No Auth"})
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_project_missing_name(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(BASE + "/", json={}, headers=auth_headers)
        assert response.status_code == 422


class TestListProjects:
    @pytest.mark.asyncio
    async def test_list_projects(
        self, client: AsyncClient, auth_headers: dict, test_project
    ):
        response = await client.get(BASE + "/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(p["name"] == "Test Project" for p in data)

    @pytest.mark.asyncio
    async def test_list_projects_empty(
        self, client: AsyncClient, other_auth_headers: dict
    ):
        """멤버가 아닌 사용자는 빈 목록"""
        response = await client.get(BASE + "/", headers=other_auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_projects_unauthorized(self, client: AsyncClient):
        response = await client.get(BASE + "/")
        assert response.status_code == 401


class TestGetProject:
    @pytest.mark.asyncio
    async def test_get_project_success(
        self, client: AsyncClient, auth_headers: dict, test_project
    ):
        response = await client.get(
            f"{BASE}/{test_project.id}", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Project"
        assert "members" in data

    @pytest.mark.asyncio
    async def test_get_project_non_member(
        self, client: AsyncClient, other_auth_headers: dict, test_project
    ):
        response = await client.get(
            f"{BASE}/{test_project.id}", headers=other_auth_headers
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_project_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.get(f"{BASE}/99999", headers=auth_headers)
        assert response.status_code == 404


class TestUpdateProject:
    @pytest.mark.asyncio
    async def test_update_project_owner(
        self, client: AsyncClient, auth_headers: dict, test_project
    ):
        response = await client.put(
            f"{BASE}/{test_project.id}",
            json={"name": "Updated"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated"

    @pytest.mark.asyncio
    async def test_update_project_partial(
        self, client: AsyncClient, auth_headers: dict, test_project
    ):
        """description만 수정"""
        response = await client.put(
            f"{BASE}/{test_project.id}",
            json={"description": "new desc"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["description"] == "new desc"
        assert response.json()["name"] == "Test Project"

    @pytest.mark.asyncio
    async def test_update_project_member_forbidden(
        self,
        client: AsyncClient,
        other_auth_headers: dict,
        other_user,
        test_project,
        db_session,
    ):
        """일반 멤버는 수정 불가"""
        from app.models.project import ProjectMember, ProjectRole

        m = ProjectMember(
            user_id=other_user.id,
            project_id=test_project.id,
            role=ProjectRole.member,
        )
        db_session.add(m)
        await db_session.flush()

        response = await client.put(
            f"{BASE}/{test_project.id}",
            json={"name": "Hack"},
            headers=other_auth_headers,
        )
        assert response.status_code == 403


class TestDeleteProject:
    @pytest.mark.asyncio
    async def test_delete_project_owner(
        self, client: AsyncClient, auth_headers: dict, test_project
    ):
        response = await client.delete(
            f"{BASE}/{test_project.id}", headers=auth_headers
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_project_admin_forbidden(
        self,
        client: AsyncClient,
        other_auth_headers: dict,
        other_user,
        test_project,
        db_session,
    ):
        """admin도 프로젝트 삭제 불가 (owner만)"""
        from app.models.project import ProjectMember, ProjectRole

        m = ProjectMember(
            user_id=other_user.id,
            project_id=test_project.id,
            role=ProjectRole.admin,
        )
        db_session.add(m)
        await db_session.flush()

        response = await client.delete(
            f"{BASE}/{test_project.id}", headers=other_auth_headers
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_project_non_member_forbidden(
        self, client: AsyncClient, other_auth_headers: dict, test_project
    ):
        response = await client.delete(
            f"{BASE}/{test_project.id}", headers=other_auth_headers
        )
        assert response.status_code == 403


class TestAddMember:
    @pytest.mark.asyncio
    async def test_add_member_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project,
        other_user,
    ):
        response = await client.post(
            f"{BASE}/{test_project.id}/members",
            json={"user_id": other_user.id},
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["user_id"] == other_user.id
        assert response.json()["role"] == "member"

    @pytest.mark.asyncio
    async def test_add_member_regular_member_forbidden(
        self,
        client: AsyncClient,
        other_auth_headers: dict,
        other_user,
        test_project,
        db_session,
    ):
        """일반 멤버는 멤버 추가 불가"""
        from app.models.project import ProjectMember, ProjectRole

        m = ProjectMember(
            user_id=other_user.id,
            project_id=test_project.id,
            role=ProjectRole.member,
        )
        db_session.add(m)
        await db_session.flush()

        response = await client.post(
            f"{BASE}/{test_project.id}/members",
            json={"user_id": 999},
            headers=other_auth_headers,
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_add_member_duplicate(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project,
        test_user,
    ):
        """이미 멤버인 사용자 추가 시 400"""
        response = await client.post(
            f"{BASE}/{test_project.id}/members",
            json={"user_id": test_user.id},
            headers=auth_headers,
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_add_member_user_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project,
    ):
        response = await client.post(
            f"{BASE}/{test_project.id}/members",
            json={"user_id": 99999},
            headers=auth_headers,
        )
        assert response.status_code == 404

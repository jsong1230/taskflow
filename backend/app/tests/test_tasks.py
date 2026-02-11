import pytest
from httpx import AsyncClient


def tasks_url(project_id: int) -> str:
    return f"/api/v1/projects/{project_id}/tasks"


def task_url(project_id: int, task_id: int) -> str:
    return f"/api/v1/projects/{project_id}/tasks/{task_id}"


def comments_url(project_id: int, task_id: int) -> str:
    return f"/api/v1/projects/{project_id}/tasks/{task_id}/comments"


class TestCreateTask:
    @pytest.mark.asyncio
    async def test_create_task_success(
        self, client: AsyncClient, auth_headers: dict, test_project
    ):
        response = await client.post(
            tasks_url(test_project.id),
            json={"title": "New Task"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Task"
        assert data["status"] == "todo"
        assert data["priority"] == "medium"

    @pytest.mark.asyncio
    async def test_create_task_with_assignee(
        self, client: AsyncClient, auth_headers: dict, test_project, test_user
    ):
        response = await client.post(
            tasks_url(test_project.id),
            json={"title": "Assigned", "assignee_id": test_user.id},
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["assignee_id"] == test_user.id

    @pytest.mark.asyncio
    async def test_create_task_non_member(
        self, client: AsyncClient, other_auth_headers: dict, test_project
    ):
        response = await client.post(
            tasks_url(test_project.id),
            json={"title": "Nope"},
            headers=other_auth_headers,
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_task_project_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.post(
            tasks_url(99999),
            json={"title": "No Project"},
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestListTasks:
    @pytest.mark.asyncio
    async def test_list_tasks(
        self, client: AsyncClient, auth_headers: dict, test_project, test_task
    ):
        response = await client.get(
            tasks_url(test_project.id), headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_list_tasks_filter_status(
        self, client: AsyncClient, auth_headers: dict, test_project, test_task
    ):
        response = await client.get(
            tasks_url(test_project.id),
            params={"status": "todo"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        for t in response.json():
            assert t["status"] == "todo"

    @pytest.mark.asyncio
    async def test_list_tasks_filter_priority(
        self, client: AsyncClient, auth_headers: dict, test_project, test_task
    ):
        response = await client.get(
            tasks_url(test_project.id),
            params={"priority": "medium"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        for t in response.json():
            assert t["priority"] == "medium"

    @pytest.mark.asyncio
    async def test_list_tasks_filter_assignee(
        self, client: AsyncClient, auth_headers: dict, test_project, test_user, db_session
    ):
        from app.models.task import Task

        task = Task(
            title="Assigned Task",
            project_id=test_project.id,
            assignee_id=test_user.id,
        )
        db_session.add(task)
        await db_session.flush()

        response = await client.get(
            tasks_url(test_project.id),
            params={"assignee_id": test_user.id},
            headers=auth_headers,
        )
        assert response.status_code == 200
        for t in response.json():
            assert t["assignee_id"] == test_user.id

    @pytest.mark.asyncio
    async def test_list_tasks_sort_by_title(
        self, client: AsyncClient, auth_headers: dict, test_project, db_session
    ):
        from app.models.task import Task

        for title in ["Charlie", "Alpha", "Bravo"]:
            db_session.add(Task(title=title, project_id=test_project.id))
        await db_session.flush()

        response = await client.get(
            tasks_url(test_project.id),
            params={"sort_by": "title", "sort_order": "asc"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        titles = [t["title"] for t in response.json()]
        assert titles == sorted(titles)

    @pytest.mark.asyncio
    async def test_list_tasks_non_member(
        self, client: AsyncClient, other_auth_headers: dict, test_project
    ):
        response = await client.get(
            tasks_url(test_project.id), headers=other_auth_headers
        )
        assert response.status_code == 403


class TestGetTask:
    @pytest.mark.asyncio
    async def test_get_task_success(
        self, client: AsyncClient, auth_headers: dict, test_project, test_task
    ):
        response = await client.get(
            task_url(test_project.id, test_task.id), headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Test Task"

    @pytest.mark.asyncio
    async def test_get_task_not_found(
        self, client: AsyncClient, auth_headers: dict, test_project
    ):
        response = await client.get(
            task_url(test_project.id, 99999), headers=auth_headers
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_task_wrong_project(
        self, client: AsyncClient, auth_headers: dict, test_project, test_task, db_session
    ):
        """다른 프로젝트의 태스크 ID로 조회 시 404"""
        from app.models.project import Project, ProjectMember, ProjectRole

        project2 = Project(name="Other", owner_id=test_project.owner_id)
        db_session.add(project2)
        await db_session.flush()
        db_session.add(
            ProjectMember(
                user_id=test_project.owner_id,
                project_id=project2.id,
                role=ProjectRole.owner,
            )
        )
        await db_session.flush()

        response = await client.get(
            task_url(project2.id, test_task.id), headers=auth_headers
        )
        assert response.status_code == 404


class TestUpdateTask:
    @pytest.mark.asyncio
    async def test_update_task_success(
        self, client: AsyncClient, auth_headers: dict, test_project, test_task
    ):
        response = await client.put(
            task_url(test_project.id, test_task.id),
            json={"title": "Updated Task", "status": "in_progress"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Task"
        assert data["status"] == "in_progress"

    @pytest.mark.asyncio
    async def test_update_task_partial(
        self, client: AsyncClient, auth_headers: dict, test_project, test_task
    ):
        response = await client.put(
            task_url(test_project.id, test_task.id),
            json={"description": "new desc"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["description"] == "new desc"
        assert response.json()["title"] == "Test Task"

    @pytest.mark.asyncio
    async def test_update_task_not_found(
        self, client: AsyncClient, auth_headers: dict, test_project
    ):
        response = await client.put(
            task_url(test_project.id, 99999),
            json={"title": "X"},
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestUpdateTaskStatus:
    @pytest.mark.asyncio
    async def test_update_status_success(
        self, client: AsyncClient, auth_headers: dict, test_project, test_task
    ):
        response = await client.patch(
            task_url(test_project.id, test_task.id) + "/status",
            json={"status": "in_progress"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"

    @pytest.mark.asyncio
    async def test_update_status_invalid(
        self, client: AsyncClient, auth_headers: dict, test_project, test_task
    ):
        response = await client.patch(
            task_url(test_project.id, test_task.id) + "/status",
            json={"status": "invalid_status"},
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestDeleteTask:
    @pytest.mark.asyncio
    async def test_delete_task_success(
        self, client: AsyncClient, auth_headers: dict, test_project, test_task
    ):
        response = await client.delete(
            task_url(test_project.id, test_task.id), headers=auth_headers
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_task_not_found(
        self, client: AsyncClient, auth_headers: dict, test_project
    ):
        response = await client.delete(
            task_url(test_project.id, 99999), headers=auth_headers
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_task_non_member(
        self, client: AsyncClient, other_auth_headers: dict, test_project, test_task
    ):
        response = await client.delete(
            task_url(test_project.id, test_task.id), headers=other_auth_headers
        )
        assert response.status_code == 403


class TestCreateComment:
    @pytest.mark.asyncio
    async def test_create_comment_success(
        self, client: AsyncClient, auth_headers: dict, test_project, test_task, test_user
    ):
        response = await client.post(
            comments_url(test_project.id, test_task.id),
            json={"content": "Great work!"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Great work!"
        assert data["author_id"] == test_user.id
        assert data["task_id"] == test_task.id

    @pytest.mark.asyncio
    async def test_create_comment_non_member(
        self, client: AsyncClient, other_auth_headers: dict, test_project, test_task
    ):
        response = await client.post(
            comments_url(test_project.id, test_task.id),
            json={"content": "Nope"},
            headers=other_auth_headers,
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_comment_empty_content(
        self, client: AsyncClient, auth_headers: dict, test_project, test_task
    ):
        response = await client.post(
            comments_url(test_project.id, test_task.id),
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestListComments:
    @pytest.mark.asyncio
    async def test_list_comments_success(
        self, client: AsyncClient, auth_headers: dict, test_project, test_task
    ):
        # 댓글 2개 생성
        await client.post(
            comments_url(test_project.id, test_task.id),
            json={"content": "First"},
            headers=auth_headers,
        )
        await client.post(
            comments_url(test_project.id, test_task.id),
            json={"content": "Second"},
            headers=auth_headers,
        )

        response = await client.get(
            comments_url(test_project.id, test_task.id),
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["content"] == "First"
        assert data[1]["content"] == "Second"

    @pytest.mark.asyncio
    async def test_list_comments_empty(
        self, client: AsyncClient, auth_headers: dict, test_project, test_task
    ):
        response = await client.get(
            comments_url(test_project.id, test_task.id),
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_comments_non_member(
        self, client: AsyncClient, other_auth_headers: dict, test_project, test_task
    ):
        response = await client.get(
            comments_url(test_project.id, test_task.id),
            headers=other_auth_headers,
        )
        assert response.status_code == 403

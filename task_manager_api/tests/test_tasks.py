import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_task(client: AsyncClient, auth_headers):
    """Тест создания задачи"""
    response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Test Task",
            "description": "Test description",
            "completed": False
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test description"
    assert data["completed"] == False
    assert "id" in data
    assert "owner_id" in data

@pytest.mark.asyncio
async def test_create_task_unauthorized(client: AsyncClient):
    """Тест создания задачи без авторизации"""
    response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Test Task",
            "description": "Test description"
        }
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_tasks(client: AsyncClient, auth_headers):
    """Тест получения списка задач"""
    # Создаем задачу
    await client.post(
        "/api/v1/tasks",
        json={"title": "Task 1", "description": "Description 1"},
        headers=auth_headers
    )
    
    response = await client.get("/api/v1/tasks", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert len(data["items"]) > 0

@pytest.mark.asyncio
async def test_get_tasks_pagination(client: AsyncClient, auth_headers):
    """Тест пагинации задач"""
    # Создаем несколько задач
    for i in range(5):
        await client.post(
            "/api/v1/tasks",
            json={"title": f"Task {i}"},
            headers=auth_headers
        )
    
    response = await client.get(
        "/api/v1/tasks?page=1&page_size=2",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2

@pytest.mark.asyncio
async def test_get_tasks_filter_completed(client: AsyncClient, auth_headers):
    """Тест фильтрации задач по статусу"""
    # Создаем завершенную и незавершенную задачи
    await client.post(
        "/api/v1/tasks",
        json={"title": "Completed Task", "completed": True},
        headers=auth_headers
    )
    await client.post(
        "/api/v1/tasks",
        json={"title": "Incomplete Task", "completed": False},
        headers=auth_headers
    )
    
    response = await client.get(
        "/api/v1/tasks?completed=true",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert all(task["completed"] for task in data["items"])

@pytest.mark.asyncio
async def test_get_task_by_id(client: AsyncClient, auth_headers):
    """Тест получения задачи по ID"""
    # Создаем задачу
    create_response = await client.post(
        "/api/v1/tasks",
        json={"title": "Specific Task", "description": "Specific description"},
        headers=auth_headers
    )
    task_id = create_response.json()["id"]
    
    # Получаем задачу
    response = await client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Specific Task"

@pytest.mark.asyncio
async def test_get_task_not_found(client: AsyncClient, auth_headers):
    """Тест получения несуществующей задачи"""
    response = await client.get("/api/v1/tasks/99999", headers=auth_headers)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_task(client: AsyncClient, auth_headers):
    """Тест обновления задачи"""
    # Создаем задачу
    create_response = await client.post(
        "/api/v1/tasks",
        json={"title": "Original Title", "completed": False},
        headers=auth_headers
    )
    task_id = create_response.json()["id"]
    
    # Обновляем задачу
    response = await client.put(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Updated Title", "completed": True},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["completed"] == True

@pytest.mark.asyncio
async def test_delete_task(client: AsyncClient, auth_headers):
    """Тест удаления задачи"""
    # Создаем задачу
    create_response = await client.post(
        "/api/v1/tasks",
        json={"title": "Task to Delete"},
        headers=auth_headers
    )
    task_id = create_response.json()["id"]
    
    # Удаляем задачу
    response = await client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 204
    
    # Проверяем, что задача удалена
    get_response = await client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_user_cannot_access_other_user_task(client: AsyncClient, db_session, test_user):
    """Тест: пользователь не может получить задачу другого пользователя"""
    from app.core.security import get_password_hash
    from app.db.models import User, UserRole, Task
    
    # Создаем второго пользователя
    other_user = User(
        email="other@example.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.USER
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)
    
    # Создаем задачу от имени другого пользователя напрямую в БД
    other_task = Task(
        title="Other User Task",
        owner_id=other_user.id
    )
    db_session.add(other_task)
    await db_session.commit()
    await db_session.refresh(other_task)
    
    # Получаем токен для первого пользователя
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": test_user.email, "password": "testpassword123"}
    )
    user_token = login_response.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    # Пытаемся получить задачу другого пользователя
    response = await client.get(
        f"/api/v1/tasks/{other_task.id}",
        headers=user_headers
    )
    # Должен вернуть 404, так как задача принадлежит другому пользователю
    assert response.status_code == 404

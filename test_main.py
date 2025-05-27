import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date

from main import app, get_db
from db.database import engine, init_db, SessionLocal
from models.models import Base
from schemas.task_schema import TaskCreate, Task


# Initialize test database
init_db()


# Create test client
@pytest.fixture
def client():
    return TestClient(app)


# Override database dependency for tests
def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# Create test client
@pytest.fixture
def client():
    return TestClient(app)


# Test cases
def test_create_task(client):
    response = client.post(
        "/task",
        json={"name": "Test Task", "description": "Test Description"}
    )
    assert response.status_code == 200
    task = response.json()
    assert task["name"] == "Test Task"
    assert task["description"] == "Test Description"
    assert task["status"] is False
    assert task["parent_id"] is None


def test_read_task(client):
    # Create a task first
    create_response = client.post(
        "/task",
        json={"name": "Test Task", "description": "Test Description"}
    )
    task_id = create_response.json()["id"]

    # Test get_task
    response = client.get(f"/task/{task_id}")
    assert response.status_code == 200
    task = response.json()
    assert task["id"] == task_id
    assert task["name"] == "Test Task"
    assert task["description"] == "Test Description"

    # Test task not found
    response = client.get("/task/999999")
    assert response.status_code == 404


def test_update_task(client):
    # Create a task first
    create_response = client.post(
        "/task",
        json={"name": "Test Task", "description": "Test Description"}
    )
    task_id = create_response.json()["id"]

    # Update the task
    update_response = client.put(
        f"/task/{task_id}",
        json={
            "id": task_id,
            "name": "Updated Task",
            "description": "Updated Description",
            "status": True,
            "parent_id": None
        }
    )
    assert update_response.status_code == 200
    updated_task = update_response.json()
    assert updated_task["name"] == "Updated Task"
    assert updated_task["description"] == "Updated Description"
    assert updated_task["status"] is True
    assert updated_task["parent_id"] is None

    # Verify update
    verify_response = client.get(f"/task/{task_id}")
    assert verify_response.status_code == 200
    assert verify_response.json()["name"] == "Updated Task"
    assert verify_response.json()["description"] == "Updated Description"
    assert verify_response.json()["status"] is True
    assert verify_response.json()["parent_id"] is None

    # Test update non-existent task
    response = client.put(
        "/task/999999",
        json={
            "id": 999999,
            "name": "Non-existent Task",
            "description": "Test",
            "status": False,
            "parent_id": None
        }
    )
    assert response.status_code == 404


def test_delete_task(client):
    # Create a task with subtasks
    parent_response = client.post(
        "/task",
        json={"name": "Parent Task", "description": "Parent Description"}
    )
    parent_id = parent_response.json()["id"]
    
    # Create subtasks
    subtask1_response = client.post(
        f"/task/{parent_id}/subtask",
        json={"name": "Subtask 1", "description": "Subtask Description"}
    )
    
    subtask2_response = client.post(
        f"/task/{parent_id}/subtask",
        json={"name": "Subtask 2", "description": "Subtask Description"}
    )
    
    # Delete parent task
    delete_response = client.delete(f"/task/{parent_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["detail"] == "Task deleted successfully"

    # Verify parent task is marked as deleted
    response = client.get(f"/task/{parent_id}")
    assert response.status_code == 200
    assert response.json()["end_date"] is not None

    # Verify subtasks are marked as deleted
    subtask1_id = subtask1_response.json()["id"]
    subtask2_id = subtask2_response.json()["id"]
    
    response = client.get(f"/task/{subtask1_id}")
    assert response.status_code == 200
    assert response.json()["end_date"] is not None
    
    response = client.get(f"/task/{subtask2_id}")
    assert response.status_code == 200
    assert response.json()["end_date"] is not None

    # Test deleting non-existent task
    response = client.delete("/task/999999")
    assert response.status_code == 404


def test_read_all_tasks(client):
    # Create multiple tasks
    task1_response = client.post(
        "/task",
        json={"name": "Task 1", "description": "Description 1"}
    )
    task2_response = client.post(
        "/task",
        json={"name": "Task 2", "description": "Description 2"}
    )
    
    # Get all tasks
    response = client.get("/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) >= 2
    assert any(task["name"] == "Task 1" for task in tasks)
    assert any(task["name"] == "Task 2" for task in tasks)


def test_create_subtask(client):
    # Create parent task
    parent_response = client.post(
        "/task",
        json={"name": "Parent Task", "description": "Parent Description"}
    )
    parent_id = parent_response.json()["id"]
    
    # Create subtask
    response = client.post(
        f"/task/{parent_id}/subtask",
        json={"name": "Subtask", "description": "Subtask Description"}
    )
    assert response.status_code == 200
    subtask = response.json()
    assert subtask["name"] == "Subtask"
    assert subtask["description"] == "Subtask Description"
    assert subtask["parent_id"] == parent_id
    assert subtask["status"] is False

    # Test creating subtask with non-existent parent
    response = client.post(
        "/task/999999/subtask",
        json={"name": "Subtask"}
    )
    assert response.status_code == 404


def test_read_subtasks(client):
    # Create parent task and subtasks
    parent_response = client.post(
        "/task",
        json={"name": "Parent Task", "description": "Parent Description"}
    )
    parent_id = parent_response.json()["id"]
    
    subtask1_response = client.post(
        f"/task/{parent_id}/subtask",
        json={"name": "Subtask 1", "description": "Description 1"}
    )
    
    subtask2_response = client.post(
        f"/task/{parent_id}/subtask",
        json={"name": "Subtask 2", "description": "Description 2"}
    )
    
    # Get subtasks
    response = client.get(f"/task/{parent_id}/subtasks")
    assert response.status_code == 200
    subtasks = response.json()
    assert len(subtasks) == 2
    assert any(subtask["name"] == "Subtask 1" for subtask in subtasks)
    assert any(subtask["name"] == "Subtask 2" for subtask in subtasks)

    # Test getting subtasks for non-existent task
    response = client.get("/task/999999/subtasks")
    assert response.status_code == 404


def test_update_subtask(client):
    # Create parent task and subtask
    parent_response = client.post(
        "/task",
        json={"name": "Parent Task", "description": "Parent Description"}
    )
    parent_id = parent_response.json()["id"]
    
    subtask_response = client.post(
        f"/task/{parent_id}/subtask",
        json={"name": "Subtask", "description": "Subtask Description"}
    )
    subtask_id = subtask_response.json()["id"]
    
    # Update subtask
    update_response = client.put(
        f"/subtask/{subtask_id}",
        json={
            "name": "Updated Subtask",
            "description": "Updated Description",
            "status": True
        }
    )
    assert update_response.status_code == 200
    updated_subtask = update_response.json()
    assert updated_subtask["name"] == "Updated Subtask"
    assert updated_subtask["description"] == "Updated Description"
    assert updated_subtask["status"] is True
    assert updated_subtask["parent_id"] == parent_id

    # Verify update
    verify_response = client.get(f"/task/{subtask_id}")
    assert verify_response.status_code == 200
    assert verify_response.json()["name"] == "Updated Subtask"
    assert verify_response.json()["description"] == "Updated Description"
    assert verify_response.json()["status"] is True

    # Test update non-existent subtask
    response = client.put(
        "/subtask/999999",
        json={"name": "Test"}
    )
    assert response.status_code == 404


def test_delete_subtask(client):
    # Create parent task and subtask
    parent_response = client.post(
        "/task",
        json={"name": "Parent Task", "description": "Parent Description"}
    )
    parent_id = parent_response.json()["id"]
    
    subtask_response = client.post(
        f"/task/{parent_id}/subtask",
        json={"name": "Subtask", "description": "Subtask Description"}
    )
    subtask_id = subtask_response.json()["id"]
    
    # Delete subtask
    delete_response = client.delete(f"/subtask/{subtask_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["detail"] == "Subtask deleted successfully"

    # Verify subtask is marked as deleted
    response = client.get(f"/subtask/{subtask_id}")
    assert response.status_code == 200
    assert response.json()["end_date"] is not None

    # Test deleting non-existent subtask
    response = client.delete("/subtask/999999")
    assert response.status_code == 404


def test_get_task_progress(client):
    # Create parent task and subtasks
    parent_response = client.post(
        "/task",
        json={"name": "Parent Task", "description": "Parent Description"}
    )
    parent_id = parent_response.json()["id"]
    
    # Create subtasks
    subtask1_response = client.post(
        f"/task/{parent_id}/subtask",
        json={"name": "Subtask 1", "description": "Description 1"}
    )
    
    subtask2_response = client.post(
        f"/task/{parent_id}/subtask",
        json={"name": "Subtask 2", "description": "Description 2"}
    )
    
    # Mark one subtask as completed by setting status to True
    subtask1_id = subtask1_response.json()["id"]
    client.put(
        f"/task/{subtask1_id}",
        json={
            "id": subtask1_id,
            "name": "Subtask 1",
            "description": "Description 1",
            "parent_id": parent_id,
            "status": True
        }
    )
    
    # Get progress
    response = client.get(f"/task/{parent_id}/progress")
    assert response.status_code == 200
    progress = response.json()
    assert progress["progress"] == 50.0

    # Test progress for non-existent task
    response = client.get("/task/999999/progress")
    assert response.status_code == 404


def test_ping(client):
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "successful!"}

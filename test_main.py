import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Base
from db.database import init_db 
from main import app


# Set up in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create all tables in the test database
@pytest.fixture(scope="module")
def test_db():
  Base.metadata.create_all(bind=engine)
  yield TestingSessionLocal()
  Base.metadata.drop_all(bind=engine)


@app.dependency
def override_get_db():
  db = TestingSessionLocal()
  try:
    yield db
  finally:
    db.close()


app.dependency_overrides[init_db] = override_get_db


@pytest.mark.asyncio
async def test_read_task(test_db):
  async with AsyncClient(app=app, base_url="http://test") as client:
    response = await client.post("/tasks/", json={"name": "Test Task", "description": "Description"})
    task_id = response.json()["id"]

    # Test get_task
    response = await client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    task_data = response.json()
    assert task_data["id"] == task_id
    assert task_data["name"] == "Test Task"
    assert task_data["description"] == "Description"

@pytest.mark.asyncio
async def test_update_task(test_db):
  async with AsyncClient(app=app, base_url="http://test") as client:
    response = await client.post("/tasks/", json={"name": "Update Task", "description": "Desc"})
    task_id = response.json()["id"]
    
    # Update the task
    update_response = await client.put(f"/tasks/{task_id}", json={"name": "Updated Task", "description": "Updated Desc"})
    assert update_response.status_code == 200
    updated_task = update_response.json()
    assert updated_task["name"] == "Updated Task"
    assert updated_task["description"] == "Updated Desc"

    verify_response = await client.get(f"/tasks/{task_id}")
    assert verify_response.status_code == 200
    assert verify_response.json()["name"] == "Updated Task"
    assert verify_response.json()["description"] == "Updated Desc"
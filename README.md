# Todd's Todo List

A FastAPI-based todo list application with task management capabilities.

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Run the application:
```bash
poetry run uvicorn main:app --reload
```

The application will be available at `http://127.0.0.1:8000`

## API Documentation

### Task Management

#### Create Task
```bash
curl --location 'http://127.0.0.1:8000/task' \
--header 'Content-Type: application/json' \
--data '{
    "name": "New Task",
    "description": "Description of the task",
    "parent_id": null,
    "status": false
}'
```

#### Get Task
```bash
curl --location 'http://127.0.0.1:8000/task/{task_id}'
```

#### Update Task
```bash
curl --location --request PUT 'http://127.0.0.1:8000/task/{task_id}' \
--header 'Content-Type: application/json' \
--data '{
    "name": "Updated Task Name",
    "description": "Updated Description",
    "parent_id": null,
    "status": true
}'
```

#### Delete Task
```bash
curl --location --request DELETE 'http://127.0.0.1:8000/task/{task_id}'
```

#### List All Tasks
```bash
curl --location 'http://127.0.0.1:8000/tasks?skip=0&limit=100'
```

### Subtask Management

#### Create Subtask
```bash
curl --location 'http://127.0.0.1:8000/task/{parent_task_id}/subtask' \
--header 'Content-Type: application/json' \
--data '{
    "name": "Subtask Name",
    "description": "Subtask Description",
    "status": false
}'
```

#### Get Subtasks
```bash
curl --location 'http://127.0.0.1:8000/task/{parent_task_id}/subtasks'
```

#### Update Subtask
```bash
curl --location --request PUT 'http://127.0.0.1:8000/subtask/{subtask_id}' \
--header 'Content-Type: application/json' \
--data '{
    "name": "Updated Subtask Name",
    "description": "Updated Description",
    "status": true
}'
```

#### Delete Subtask
```bash
curl --location --request DELETE 'http://127.0.0.1:8000/subtask/{subtask_id}'
```

#### Get Single Subtask
```bash
curl --location 'http://127.0.0.1:8000/subtask/{subtask_id}'
```

### Task Progress

#### Get Task Progress
```bash
curl --location 'http://127.0.0.1:8000/task/{task_id}/progress'
```

## API Response Format
All successful responses will return JSON objects. Error responses will include an error message and HTTP status code.

## Notes
- Replace `{task_id}` and `{subtask_id}` with actual task/subtask IDs in the curl commands
- All dates are returned in ISO format with timezone information
- Tasks are soft-deleted by setting their end_date
- Parent tasks can have multiple subtasks
- Subtasks cannot have their own subtasks
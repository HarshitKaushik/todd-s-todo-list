# Todd's Todo List
# @author harshit kaushik

## To run the application

```bash
poetry run uvicorn main:app --reload
```

## curl commands

```bash

curl --location 'http://127.0.0.1:8000/task' \
--header 'Content-Type: application/json' \
--data '{
    "name": "first task",
    "description": "first task description"
}'

```
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_todo():
    # given
    payload = {
        "content": "pytest todo"
    }

    # when
    response = client.post("/todos", json=payload)

    # then
    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["content"] == "pytest todo"
    assert "created_at" in data

def test_get_todos():
    # given: 하나 미리 생성
    client.post("/todos", json={"content": "list test"})

    # when
    response = client.get("/todos")

    # then
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    todo = data[0]
    assert "id" in todo
    assert "content" in todo
    assert "created_at" in todo
    
def test_delete_todo():
    # given: 삭제할 todo 생성
    create_response = client.post("/todos", json={"content": "delete target"})
    todo_id = create_response.json()["id"]

    # when: 삭제 요청
    delete_response = client.delete(f"/todos/{todo_id}")

    # then: 상태 코드만 확인
    assert delete_response.status_code == 200

    # and: 다시 조회했을 때 없어야 함
    list_response = client.get("/todos")
    todos = list_response.json()

    ids = [t["id"] for t in todos]
    assert todo_id not in ids
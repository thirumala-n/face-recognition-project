import pytest
from fastapi import status

def test_register_student_success(client):
    payload = {
        "student_id": "STU101",
        "name": "Jane Doe"
    }
    response = client.post("/api/v1/students", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["student_id"] == "STU101"
    assert data["name"] == "Jane Doe"
    assert "id" in data
    assert "created_at" in data

def test_register_duplicate_student_fails(client):
    payload = {
        "student_id": "STU102",
        "name": "Mark Smith"
    }
    # First registration
    res1 = client.post("/api/v1/students", json=payload)
    assert res1.status_code == status.HTTP_201_CREATED

    # Duplicate registration
    res2 = client.post("/api/v1/students", json=payload)
    assert res2.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in res2.json()["detail"]

def test_register_invalid_student_id(client):
    # Student ID with forbidden characters
    payload = {
        "student_id": "STU@103!!",
        "name": "Invalid ID"
    }
    response = client.post("/api/v1/students", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_register_empty_name(client):
    payload = {
        "student_id": "STU104",
        "name": "   "
    }
    response = client.post("/api/v1/students", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_get_student_by_id(client):
    client.post("/api/v1/students", json={"student_id": "STU105", "name": "Alice Wonderland"})
    response = client.get("/api/v1/students/STU105")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["student_id"] == "STU105"
    assert response.json()["name"] == "Alice Wonderland"

def test_get_nonexistent_student(client):
    response = client.get("/api/v1/students/NON_EXISTENT_ID")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_list_students(client):
    client.post("/api/v1/students", json={"student_id": "STU106", "name": "Bob Marley"})
    client.post("/api/v1/students", json={"student_id": "STU107", "name": "Charlie Chaplin"})

    response = client.get("/api/v1/students")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2
    student_ids = [s["student_id"] for s in data]
    assert "STU106" in student_ids
    assert "STU107" in student_ids

def test_delete_student(client):
    client.post("/api/v1/students", json={"student_id": "STU108", "name": "David Copperfield"})

    del_res = client.delete("/api/v1/students/STU108")
    assert del_res.status_code == status.HTTP_200_OK
    assert del_res.json()["student_id"] == "STU108"

    # Verify student is gone
    get_res = client.get("/api/v1/students/STU108")
    assert get_res.status_code == status.HTTP_404_NOT_FOUND

def test_delete_nonexistent_student(client):
    response = client.delete("/api/v1/students/UNKNOWN_ID_999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

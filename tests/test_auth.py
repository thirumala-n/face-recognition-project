import pytest
from fastapi import status

def test_register_user_success(client):
    payload = {
        "full_name": "Dr. Alan Grant",
        "email": "alan.grant@jurassic.edu",
        "username": "alangrant",
        "password": "Password123!"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "alan.grant@jurassic.edu"
    assert data["user"]["username"] == "alangrant"
    assert data["user"]["full_name"] == "Dr. Alan Grant"
    assert "password_hash" not in data["user"]

def test_register_duplicate_email_fails(client):
    payload1 = {
        "full_name": "Ellie Sattler",
        "email": "ellie@jurassic.edu",
        "username": "ellie_paleo",
        "password": "Password123!"
    }
    res1 = client.post("/api/v1/auth/register", json=payload1)
    assert res1.status_code == status.HTTP_201_CREATED

    payload2 = {
        "full_name": "Ellie Duplicate",
        "email": "ellie@jurassic.edu",
        "username": "ellie_dup",
        "password": "Password123!"
    }
    res2 = client.post("/api/v1/auth/register", json=payload2)
    assert res2.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in res2.json()["detail"]

def test_register_duplicate_username_fails(client):
    payload1 = {
        "full_name": "Ian Malcolm",
        "email": "ian@chaos.edu",
        "username": "ianmalcolm",
        "password": "Password123!"
    }
    res1 = client.post("/api/v1/auth/register", json=payload1)
    assert res1.status_code == status.HTTP_201_CREATED

    payload2 = {
        "full_name": "Ian Malcolm Two",
        "email": "ian2@chaos.edu",
        "username": "ianmalcolm",
        "password": "Password123!"
    }
    res2 = client.post("/api/v1/auth/register", json=payload2)
    assert res2.status_code == status.HTTP_400_BAD_REQUEST
    assert "already taken" in res2.json()["detail"]

def test_register_invalid_password_length(client):
    payload = {
        "full_name": "Short Pass User",
        "email": "short@jurassic.edu",
        "username": "shortpass",
        "password": "123"  # too short (< 6)
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_login_with_email_success(client):
    reg = client.post("/api/v1/auth/register", json={
        "full_name": "John Hammond",
        "email": "hammond@ingen.com",
        "username": "johnhammond",
        "password": "SecurePassword99"
    })
    assert reg.status_code == status.HTTP_201_CREATED

    # Login using email
    login_res = client.post("/api/v1/auth/login", json={
        "email_or_username": "hammond@ingen.com",
        "password": "SecurePassword99"
    })
    assert login_res.status_code == status.HTTP_200_OK
    data = login_res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "hammond@ingen.com"

def test_login_with_username_success(client):
    reg = client.post("/api/v1/auth/register", json={
        "full_name": "Dennis Nedry",
        "email": "nedry@ingen.com",
        "username": "magicword",
        "password": "YouDidntSayTheMagicWord!"
    })
    assert reg.status_code == status.HTTP_201_CREATED

    # Login using username
    login_res = client.post("/api/v1/auth/login", json={
        "email_or_username": "magicword",
        "password": "YouDidntSayTheMagicWord!"
    })
    assert login_res.status_code == status.HTTP_200_OK
    assert "access_token" in login_res.json()

def test_login_invalid_password_fails(client):
    client.post("/api/v1/auth/register", json={
        "full_name": "Ray Arnold",
        "email": "arnold@ingen.com",
        "username": "rayarnold",
        "password": "HoldOntoYourButts!"
    })

    login_res = client.post("/api/v1/auth/login", json={
        "email_or_username": "arnold@ingen.com",
        "password": "WrongPassword123"
    })
    assert login_res.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_me_authenticated(client):
    reg = client.post("/api/v1/auth/register", json={
        "full_name": "Henry Wu",
        "email": "wu@ingen.com",
        "username": "henrywu",
        "password": "DinoGenetics2026"
    })
    token = reg.json()["access_token"]

    # Call /me with valid Bearer token
    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_res.status_code == status.HTTP_200_OK
    data = me_res.json()
    assert data["username"] == "henrywu"
    assert data["email"] == "wu@ingen.com"

def test_get_me_unauthorized(client):
    # Without token
    res1 = client.get("/api/v1/auth/me")
    assert res1.status_code == status.HTTP_401_UNAUTHORIZED

    # With invalid token
    res2 = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid.token.xyz"})
    assert res2.status_code == status.HTTP_401_UNAUTHORIZED

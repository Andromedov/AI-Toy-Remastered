import pytest
from backend.app import app, Base, engine

@pytest.fixture
def client():
    Base.metadata.create_all(engine)
    with app.test_client() as client:
        yield client
    Base.metadata.drop_all(engine)

def register_user(client, email="test@example.com", username="testuser", password="password123"):
    return client.post("/register", json={
        "email": email,
        "username": username,
        "password": password
    })

def login_user(client, email="test@example.com", password="password123"):
    return client.post("/login", json={
        "email": email,
        "password": password
    })

def test_register_success(client):
    res = register_user(client)
    assert res.status_code == 201
    assert res.get_json()["message"] == "Користувача зареєстровано успішно!"

def test_register_duplicate_email(client):
    register_user(client)
    res = register_user(client)
    assert res.status_code == 400
    assert res.get_json()["error"] == "Користувач з таким email вже існує"

def test_login_success(client):
    register_user(client)
    res = login_user(client)
    assert res.status_code == 200
    assert "token" in res.get_json()

def test_login_failure(client):
    res = login_user(client)
    assert res.status_code == 401

def test_history_empty(client):
    register_user(client)
    login_res = login_user(client)
    token = login_res.get_json()["token"]

    res = client.get("/history", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.get_json() == {"history": []}

def test_save_and_get_api_key(client):
    register_user(client)
    token = login_user(client).get_json()["token"]

    save = client.post("/save_api_key", json={"api_key": "sk-abc"},
                       headers={"Authorization": f"Bearer {token}"})
    assert save.status_code == 200

    get = client.get("/api-key", headers={"Authorization": f"Bearer {token}"})
    assert get.status_code == 200
    assert get.get_json()["api_key"] == "sk-abc"

def test_unauthorized_ask(client):
    res = client.post("/ask", json={"question": "Що таке сонце?"})
    assert res.status_code == 401
    assert "error" in res.get_json()
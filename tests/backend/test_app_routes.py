import pytest
from backend.app import app, Session, Base, engine
from backend.models import User

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
    assert "Користувача зареєстровано" in res.get_data(as_text=True)

def test_register_duplicate_email(client):
    register_user(client)
    res = register_user(client)
    assert res.status_code == 400
    assert "вже існує" in res.get_data(as_text=True)

def test_login_success(client):
    register_user(client)
    res = login_user(client)
    assert res.status_code == 200
    assert "token" in res.get_json()

def test_login_failure(client):
    res = login_user(client)
    assert res.status_code == 401

def test_api_key_save_and_retrieve(client):
    register_user(client)
    login_res = login_user(client)
    token = login_res.get_json()["token"]

    res_save = client.post("/save_api_key", json={"api_key": "sk-test123"},
                           headers={"Authorization": f"Bearer {token}"})
    assert res_save.status_code == 200

    res_get = client.get("/api-key", headers={"Authorization": f"Bearer {token}"})
    assert res_get.status_code == 200
    assert res_get.get_json()["api_key"] == "sk-test123"
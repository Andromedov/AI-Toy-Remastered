import pytest
from flask.testing import FlaskClient
from backend.app import app

client = app.test_client()

def test_root_route():
    response = client.get("/")
    assert response.status_code == 200
    assert "status" in response.json()

def test_register_missing_fields():
    response = client.post("/register", json={})
    assert response.status_code == 400 or response.status_code == 422

def test_login_invalid_credentials():
    response = client.post("/login", json={"username": "user", "password": "wrong"})
    assert response.status_code in [401, 422, 400]
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_successful_login():
    response = client.post("/auth/token", data={
        "username": "09123456789",
        "password": "1234"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_invalid_password():
    response = client.post("/auth/token", data={
        "username": "09123456789",
        "password": "wrong"
    })
    assert response.status_code == 401

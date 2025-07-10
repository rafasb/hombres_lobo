from fastapi.testclient import TestClient
from app.main import app
import uuid
from app.database import delete_user

client = TestClient(app)

def get_token(username, password):
    resp = client.post("/login", data={"username": username, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]

def test_register_user():
    data = {
        "username": "testuser",
        "email": f"test{uuid.uuid4()}@example.com",
        "password": "testpass123"
    }
    response = client.post("/register", data=data)
    assert response.status_code == 200
    user = response.json()
    assert user["username"] == data["username"]
    assert user["email"] == data["email"]
    assert "id" in user
    assert "created_at" in user
    assert "updated_at" in user
    # Eliminar usuario creado
    assert delete_user(user["id"]) is True

def test_login_and_get_user_by_id():
    # Crear usuario primero
    data = {
        "username": "user2",
        "email": f"user2_{uuid.uuid4()}@example.com",
        "password": "pass2"
    }
    reg = client.post("/register", data=data)
    user = reg.json()
    user_id = user["id"]
    # Login para obtener token
    token = get_token(data["username"], data["password"])
    # Obtener usuario autenticado
    response = client.get(f"/users/{user_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    user2 = response.json()
    assert user2["id"] == user_id
    assert user2["username"] == data["username"]
    # Eliminar usuario creado
    assert delete_user(user_id) is True

def test_list_users_auth():
    # Crear y loguear usuario
    data = {
        "username": "userlist",
        "email": f"userlist_{uuid.uuid4()}@example.com",
        "password": "passlist"
    }
    reg = client.post("/register", data=data)
    user = reg.json()
    token = get_token(data["username"], data["password"])
    response = client.get("/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    # Eliminar usuario creado
    assert delete_user(user["id"]) is True

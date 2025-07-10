from fastapi.testclient import TestClient
from app.main import app
import os

client = TestClient(app)

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "adminpass123")

def get_token(username, password):
    resp = client.post("/login", data={"username": username, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]

def get_admin_token():
    return get_token(ADMIN_USERNAME, ADMIN_PASSWORD)

def test_admin_list_users():
    token = get_admin_token()
    response = client.get("/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_admin_get_user():
    token = get_admin_token()
    # Crear otro usuario
    data = {"username": "targetuser", "email": "target@example.com", "password": "targetpass123"}
    reg = client.post("/register", data=data)
    user = reg.json()
    response = client.get(f"/admin/users/{user['id']}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == user["id"]

def test_admin_update_user():
    token = get_admin_token()
    data = {"username": "moduser", "email": "mod@example.com", "password": "modpass123"}
    reg = client.post("/register", data=data)
    user = reg.json()
    update = {"email": "nuevoemail@example.com"}
    response = client.put(f"/admin/users/{user['id']}", json=update, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == update["email"]

def test_admin_delete_user():
    token = get_admin_token()
    data = {"username": "deluser", "email": "del@example.com", "password": "delpass123"}
    reg = client.post("/register", data=data)
    user = reg.json()
    response = client.delete(f"/admin/users/{user['id']}" , headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    get_resp = client.get(f"/admin/users/{user['id']}" , headers={"Authorization": f"Bearer {token}"})
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "banned"

def test_admin_update_user_role():
    token = get_admin_token()
    data = {"username": "promouser", "email": "promo@example.com", "password": "promopass123"}
    reg = client.post("/register", data=data)
    user = reg.json()
    response = client.put(f"/admin/users/{user['id']}/role?role=admin", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["role"] == "admin"

def test_admin_env_credentials_login():
    """Verifica que las credenciales de admin del .env permiten login y acceso a /admin/users."""
    token = get_admin_token()
    assert token is not None
    # El token debe permitir acceso a endpoint admin
    response = client.get("/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

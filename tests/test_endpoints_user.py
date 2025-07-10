from fastapi.testclient import TestClient
from app.main import app
import uuid
from app.database import delete_user, load_all_users
from app.services.game_service import delete_game

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
    data = {
        "username": "user2",
        "email": f"user2_{uuid.uuid4()}@example.com",
        "password": "pass2"
    }
    reg = client.post("/register", data=data)
    user = reg.json()
    user_id = user["id"]
    token = get_token(data["username"], data["password"])
    response = client.get(f"/users/{user_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    user2 = response.json()
    assert user2["id"] == user_id
    assert user2["username"] == data["username"]
    # Eliminar usuario creado
    assert delete_user(user_id) is True

def test_list_users_auth():
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

def test_create_and_get_game_auth():
    user_data = {
        "username": "creator",
        "email": f"creator_{uuid.uuid4()}@example.com",
        "password": "creatorpass"
    }
    reg = client.post("/register", data=user_data)
    creator = reg.json()
    token = get_token(user_data["username"], user_data["password"])
    game_data = {
        "name": "Partida Test",
        "creator_id": creator["id"],
        "max_players": 8
    }
    response = client.post("/games", json=game_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    game = response.json()
    assert game["name"] == game_data["name"]
    assert game["creator_id"] == creator["id"]
    assert game["max_players"] == 8
    gid = game["id"]
    get_resp = client.get(f"/games/{gid}", headers={"Authorization": f"Bearer {token}"})
    assert get_resp.status_code == 200
    game2 = get_resp.json()
    assert game2["id"] == gid
    assert game2["name"] == game_data["name"]
    # Eliminar partida creada
    assert delete_game(gid) is True
    # Eliminar usuario creador
    assert delete_user(creator["id"]) is True

def test_list_games_auth():
    data = {
        "username": "gamelist",
        "email": f"gamelist_{uuid.uuid4()}@example.com",
        "password": "passgamelist"
    }
    client.post("/register", data=data)
    token = get_token(data["username"], data["password"])
    response = client.get("/games", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    # Eliminar usuario creado
    users = load_all_users()
    user = next((u for u in users if u.username == data["username"]), None)
    if user:
        assert delete_user(user.id) is True

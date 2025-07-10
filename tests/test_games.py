# Pruebas de gestión de partidas

from fastapi.testclient import TestClient
from app.main import app
import uuid
from app.services.game_service import delete_game
from app.database import delete_user

client = TestClient(app)

def get_token(username, password):
    resp = client.post("/login", data={"username": username, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]

def test_create_and_get_game_auth():
    # Crear usuario y loguear
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
    # Obtener partida autenticado
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
    # Crear y loguear usuario
    data = {
        "username": "gamelist",
        "email": f"gamelist_{uuid.uuid4()}@example.com",
        "password": "passgamelist"
    }
    reg = client.post("/register", data=data)
    creator = reg.json()
    token = get_token(data["username"], data["password"])
    response = client.get("/games", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    # Eliminar usuario creado
    assert delete_user(creator["id"]) is True

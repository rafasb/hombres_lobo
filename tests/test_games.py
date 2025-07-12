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

def test_join_game():
    """Prueba que un usuario pueda unirse a una partida."""
    # Crear usuario creador
    creator_data = {
        "username": f"creator{uuid.uuid4().hex[:8]}",
        "email": f"creator_{uuid.uuid4()}@example.com",
        "password": "creatorpass"
    }
    reg = client.post("/register", data=creator_data)
    creator = reg.json()
    creator_token = get_token(creator_data["username"], creator_data["password"])
    
    # Crear usuario que se unirá
    player_data = {
        "username": f"player{uuid.uuid4().hex[:8]}",
        "email": f"player_{uuid.uuid4()}@example.com",
        "password": "playerpass"
    }
    reg2 = client.post("/register", data=player_data)
    player = reg2.json()
    player_token = get_token(player_data["username"], player_data["password"])
    
    # Crear partida
    game_data = {
        "name": "Partida para unirse",
        "creator_id": creator["id"],
        "max_players": 6
    }
    response = client.post("/games", json=game_data, headers={"Authorization": f"Bearer {creator_token}"})
    assert response.status_code == 200
    game = response.json()
    game_id = game["id"]
    
    # El jugador se une a la partida
    join_resp = client.post(f"/games/{game_id}/join", headers={"Authorization": f"Bearer {player_token}"})
    assert join_resp.status_code == 200
    assert "Te has unido a la partida exitosamente" in join_resp.json()["detail"]
    
    # Verificar que el jugador está en la partida
    get_resp = client.get(f"/games/{game_id}", headers={"Authorization": f"Bearer {creator_token}"})
    assert get_resp.status_code == 200
    updated_game = get_resp.json()
    assert len(updated_game["players"]) == 1
    assert updated_game["players"][0]["id"] == player["id"]
    
    # Intentar unirse de nuevo (debería fallar)
    join_again_resp = client.post(f"/games/{game_id}/join", headers={"Authorization": f"Bearer {player_token}"})
    assert join_again_resp.status_code == 400
    assert "ya eres jugador" in join_again_resp.json()["detail"]
    
    # Limpiar
    assert delete_game(game_id) is True
    assert delete_user(creator["id"]) is True
    assert delete_user(player["id"]) is True

def test_join_game_full():
    """Prueba que no se pueda unir a una partida llena."""
    # Crear usuarios
    creator_data = {
        "username": f"creator{uuid.uuid4().hex[:8]}",
        "email": f"creator_{uuid.uuid4()}@example.com",
        "password": "creatorpass"
    }
    reg = client.post("/register", data=creator_data)
    creator = reg.json()
    creator_token = get_token(creator_data["username"], creator_data["password"])
    
    # Crear partida con máximo 4 jugadores
    game_data = {
        "name": "Partida llena",
        "creator_id": creator["id"],
        "max_players": 4
    }
    response = client.post("/games", json=game_data, headers={"Authorization": f"Bearer {creator_token}"})
    game_id = response.json()["id"]
    
    # Crear y unir 4 jugadores
    players = []
    for i in range(4):
        player_data = {
            "username": f"player{i}{uuid.uuid4().hex[:6]}",
            "email": f"player_{i}_{uuid.uuid4()}@example.com",
            "password": f"playerpass{i}"
        }
        reg = client.post("/register", data=player_data)
        player = reg.json()
        players.append(player)
        player_token = get_token(player_data["username"], player_data["password"])
        
        join_resp = client.post(f"/games/{game_id}/join", headers={"Authorization": f"Bearer {player_token}"})
        assert join_resp.status_code == 200
    
    # Intentar unir un jugador más (debería fallar)
    extra_player_data = {
        "username": f"extra{uuid.uuid4().hex[:8]}",
        "email": f"extra_{uuid.uuid4()}@example.com",
        "password": "extrapass"
    }
    reg = client.post("/register", data=extra_player_data)
    extra_player = reg.json()
    extra_token = get_token(extra_player_data["username"], extra_player_data["password"])
    
    join_resp = client.post(f"/games/{game_id}/join", headers={"Authorization": f"Bearer {extra_token}"})
    assert join_resp.status_code == 400
    assert "partida llena" in join_resp.json()["detail"]
    
    # Limpiar
    assert delete_game(game_id) is True
    assert delete_user(creator["id"]) is True
    for player in players:
        assert delete_user(player["id"]) is True
    assert delete_user(extra_player["id"]) is True

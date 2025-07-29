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
    assert len(updated_game["players"]) == 2  # Creador + jugador que se unió
    assert updated_game["players"][0]["id"] == creator["id"]
    assert updated_game["players"][1]["id"] == player["id"]
    
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
    
    # Crear y unir 3 jugadores más (ya hay 1 creador, total será 4)
    players = []
    for i in range(3):
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

def test_assign_roles():
    """Prueba que el creador pueda iniciar el reparto de roles."""
    # Crear usuario creador
    creator_data = {
        "username": f"creator{uuid.uuid4().hex[:8]}",
        "email": f"creator_{uuid.uuid4()}@example.com",
        "password": "creatorpass"
    }
    reg = client.post("/register", data=creator_data)
    creator = reg.json()
    creator_token = get_token(creator_data["username"], creator_data["password"])
    
    # Crear partida
    game_data = {
        "name": "Partida para roles",
        "creator_id": creator["id"],
        "max_players": 18
    }
    response = client.post("/games", json=game_data, headers={"Authorization": f"Bearer {creator_token}"})
    game = response.json()
    game_id = game["id"]
    
    # Crear y unir 9 jugadores más (total 10 con el creador, mínimo requerido)
    players = []
    for i in range(9):
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
    
    # Iniciar reparto de roles
    assign_resp = client.post(f"/games/{game_id}/assign-roles", headers={"Authorization": f"Bearer {creator_token}"})
    assert assign_resp.status_code == 200
    updated_game = assign_resp.json()
    
    # Verificar que la partida cambió de estado
    assert updated_game["status"] == "started"
    assert updated_game["current_round"] == 1
    
    # Verificar que todos los jugadores tienen roles asignados
    assert len(updated_game["roles"]) == 10  # 10 jugadores total
    
    # Verificar que hay el número correcto de hombres lobo (10 // 3 = 3)
    roles_list = list(updated_game["roles"].values())
    warewolf_count = sum(1 for role_info in roles_list if role_info["role"] == "warewolf")
    assert warewolf_count == 3
    
    # Verificar que hay roles especiales
    special_roles = ["seer", "witch", "hunter", "cupid"]
    roles_present = [role_info["role"] for role_info in roles_list]
    for special_role in special_roles:
        assert special_role in roles_present
    
    # Verificar número de aldeanos (10 - 3 lobos - 4 especiales = 3 aldeanos)
    villager_count = sum(1 for role_info in roles_list if role_info["role"] == "villager")
    assert villager_count == 3
    
    # Intentar iniciar reparto de nuevo (debería fallar)
    assign_again_resp = client.post(f"/games/{game_id}/assign-roles", headers={"Authorization": f"Bearer {creator_token}"})
    assert assign_again_resp.status_code == 400
    
    # Limpiar
    assert delete_game(game_id) is True
    assert delete_user(creator["id"]) is True
    for player in players:
        assert delete_user(player["id"]) is True

def test_assign_roles_insufficient_players():
    """Prueba que no se puede iniciar el reparto con pocos jugadores."""
    # Crear usuario creador
    creator_data = {
        "username": f"creator{uuid.uuid4().hex[:8]}",
        "email": f"creator_{uuid.uuid4()}@example.com",
        "password": "creatorpass"
    }
    reg = client.post("/register", data=creator_data)
    creator = reg.json()
    creator_token = get_token(creator_data["username"], creator_data["password"])
    
    # Crear partida
    game_data = {
        "name": "Partida pocos jugadores",
        "creator_id": creator["id"],
        "max_players": 18
    }
    response = client.post("/games", json=game_data, headers={"Authorization": f"Bearer {creator_token}"})
    game = response.json()
    game_id = game["id"]
    
    # Unir solo 8 jugadores más (total 9 con el creador, menos del mínimo de 10)
    players = []
    for i in range(8):
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
    
    # Intentar iniciar reparto de roles (debería fallar)
    assign_resp = client.post(f"/games/{game_id}/assign-roles", headers={"Authorization": f"Bearer {creator_token}"})
    assert assign_resp.status_code == 400
    assert "faltan jugadores" in assign_resp.json()["detail"]
    
    # Limpiar
    assert delete_game(game_id) is True
    assert delete_user(creator["id"]) is True
    for player in players:
        assert delete_user(player["id"]) is True

def test_assign_roles_maximum_players():
    """Prueba que se puede iniciar el reparto con el máximo de jugadores (18)."""
    # Crear usuario creador
    creator_data = {
        "username": f"creator{uuid.uuid4().hex[:8]}",
        "email": f"creator_{uuid.uuid4()}@example.com",
        "password": "creatorpass"
    }
    reg = client.post("/register", data=creator_data)
    creator = reg.json()
    creator_token = get_token(creator_data["username"], creator_data["password"])
    
    # Crear partida
    game_data = {
        "name": "Partida máximos jugadores",
        "creator_id": creator["id"],
        "max_players": 18
    }
    response = client.post("/games", json=game_data, headers={"Authorization": f"Bearer {creator_token}"})
    game = response.json()
    game_id = game["id"]
    
    # Unir 17 jugadores más (total 18 con el creador, máximo permitido)
    players = []
    for i in range(17):
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
    
    # Iniciar reparto de roles (debería funcionar)
    assign_resp = client.post(f"/games/{game_id}/assign-roles", headers={"Authorization": f"Bearer {creator_token}"})
    assert assign_resp.status_code == 200
    updated_game = assign_resp.json()
    
    # Verificar que la partida cambió de estado
    assert updated_game["status"] == "started"
    assert updated_game["current_round"] == 1
    
    # Verificar que todos los jugadores tienen roles asignados
    assert len(updated_game["roles"]) == 18  # 18 jugadores total
    
    # Verificar que hay el número correcto de hombres lobo (18 // 3 = 6)
    roles_list = list(updated_game["roles"].values())
    warewolf_count = sum(1 for role_info in roles_list if role_info["role"] == "warewolf")
    assert warewolf_count == 6
    
    # Verificar que hay todos los roles especiales
    special_roles = ["seer", "witch", "hunter", "cupid"]
    roles_present = [role_info["role"] for role_info in roles_list]
    for special_role in special_roles:
        assert special_role in roles_present
    
    # Verificar número de aldeanos (18 - 6 lobos - 4 especiales = 8 aldeanos)
    villager_count = sum(1 for role_info in roles_list if role_info["role"] == "villager")
    assert villager_count == 8
    
    # Limpiar
    assert delete_game(game_id) is True
    assert delete_user(creator["id"]) is True
    for player in players:
        assert delete_user(player["id"]) is True

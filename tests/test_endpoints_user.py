from fastapi.testclient import TestClient
from app.main import app
import uuid
from app.database import delete_user, load_all_users
from app.services.game_service import delete_game
from app.database import load_game

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
    
    # Usuario regular NO debe poder acceder a lista completa de usuarios
    response = client.get("/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403  # Forbidden - solo admin puede ver lista completa
    
    # Pero SÍ debe poder acceder a su propio perfil
    response = client.get(f"/users/{user['id']}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == user["id"]
    
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

def test_leave_game_endpoint():
    # Crear usuario y loguear
    user_data = {
        "username": "jugador_leave",
        "email": "leave_{0}@example.com".format(uuid.uuid4()),
        "password": "leavepass"
    }
    reg = client.post("/register", data=user_data)
    user = reg.json()
    token = get_token(user_data["username"], user_data["password"])
    # Crear partida y añadir usuario como jugador
    game_data = {
        "name": "Partida Leave Test",
        "creator_id": user["id"],
        "max_players": 8
    }
    resp = client.post("/games", json=game_data, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    game = resp.json()
    gid = game["id"]
    # Simular que el usuario se une a la partida (añadirlo a players)
    g = load_game(gid)
    assert g is not None
    # Crear objeto User desde el diccionario
    from app.models.user import User
    from datetime import datetime
    user_obj = User(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        hashed_password=user["hashed_password"],
        status=user["status"],
        role=user["role"],
        created_at=datetime.fromisoformat(user["created_at"]) if isinstance(user["created_at"], str) else user["created_at"],
        updated_at=datetime.fromisoformat(user["updated_at"]) if isinstance(user["updated_at"], str) else user["updated_at"]
    )
    # Añadir usuario a la partida y guardar usando la función apropiada
    if not hasattr(g, 'players') or g.players is None:
        g.players = []
    g.players.append(user_obj)
    from app.database import save_game
    save_game(g)
    # Abandonar la partida
    leave_resp = client.post(f"/games/{gid}/leave", headers={"Authorization": f"Bearer {token}"})
    assert leave_resp.status_code == 200
    assert leave_resp.json()["detail"] == "Has abandonado la partida"
    # Comprobar que ya no está en la lista de jugadores
    g2 = load_game(gid)
    assert g2 is not None
    assert all((p["id"] if isinstance(p, dict) else p.id) != user["id"] for p in g2.players)
    # Limpiar datos
    from app.services.game_service import delete_game
    assert delete_game(gid) is True
    from app.database import delete_user
    assert delete_user(user["id"]) is True

def test_update_game_params_and_status_and_delete():
    # Crear usuario y loguear
    user_data = {
        "username": "creador_param",
        "email": f"param_{uuid.uuid4()}@example.com",
        "password": "parampass"
    }
    reg = client.post("/register", data=user_data)
    user = reg.json()
    token = get_token(user_data["username"], user_data["password"])
    # Crear partida
    game_data = {
        "name": "Partida Param Test",
        "creator_id": user["id"],
        "max_players": 8
    }
    resp = client.post("/games", json=game_data, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    game = resp.json()
    gid = game["id"]
    # Modificar parámetros (nombre y max_players)
    update_data = {"name": "Nueva Partida", "max_players": 10}
    upd_resp = client.put(f"/games/{gid}", json=update_data, headers={"Authorization": f"Bearer {token}"})
    assert upd_resp.status_code == 200
    updated = upd_resp.json()
    assert updated["name"] == "Nueva Partida"
    assert updated["max_players"] == 10
    # Cambiar estado a STARTED
    status_resp = client.put(f"/games/{gid}/status", json="started", headers={"Authorization": f"Bearer {token}"})
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "started"
    # Pausar la partida
    pause_resp = client.put(f"/games/{gid}/status", json="paused", headers={"Authorization": f"Bearer {token}"})
    assert pause_resp.status_code == 200
    assert pause_resp.json()["status"] == "paused"
    # Eliminar la partida (debe poder porque está pausada)
    del_resp = client.delete(f"/games/{gid}", headers={"Authorization": f"Bearer {token}"})
    assert del_resp.status_code == 200
    assert del_resp.json()["detail"] == "Partida eliminada"
    # Limpiar usuario
    from app.database import delete_user
    assert delete_user(user["id"]) is True

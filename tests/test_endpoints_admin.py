from fastapi.testclient import TestClient
from app.main import app
import os
from app.database import delete_user

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
    # Eliminar usuario creado
    assert delete_user(user["id"]) is True

def test_admin_update_user():
    token = get_admin_token()
    data = {"username": "moduser", "email": "mod@example.com", "password": "modpass123"}
    reg = client.post("/register", data=data)
    user = reg.json()
    update = {"email": "nuevoemail@example.com"}
    response = client.put(f"/admin/users/{user['id']}", json=update, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == update["email"]
    # Eliminar usuario creado
    assert delete_user(user["id"]) is True

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
    # Eliminar usuario creado (borrado lógico, pero limpiamos registro)
    assert delete_user(user["id"]) is True

def test_admin_update_user_role():
    token = get_admin_token()
    data = {"username": "promouser", "email": "promo@example.com", "password": "promopass123"}
    reg = client.post("/register", data=data)
    user = reg.json()
    response = client.put(f"/admin/users/{user['id']}/role?role=admin", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["role"] == "admin"
    # Eliminar usuario creado
    assert delete_user(user["id"]) is True

def test_admin_env_credentials_login():
    """Verifica que las credenciales de admin del .env permiten login y acceso a /admin/users."""
    token = get_admin_token()
    assert token is not None
    # El token debe permitir acceso a endpoint admin
    response = client.get("/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_admin_delete_game():
    token = get_admin_token()
    # Crear usuario y partida
    user_data = {"username": "admin_game", "email": "admin_game@example.com", "password": "adminpassgame"}
    reg = client.post("/register", data=user_data)
    creator = reg.json()
    user_token = get_token(user_data["username"], user_data["password"])
    game_data = {
        "name": "Partida Admin Test",
        "creator_id": creator["id"],
        "max_players": 8
    }
    resp = client.post("/games", json=game_data, headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 200
    game = resp.json()
    gid = game["id"]
    # Eliminar partida como admin
    del_resp = client.delete(f"/admin/games/{gid}", headers={"Authorization": f"Bearer {token}"})
    assert del_resp.status_code == 200
    assert del_resp.json()["detail"] == "Partida eliminada"
    # Comprobar que ya no existe
    get_resp = client.get(f"/games/{gid}", headers={"Authorization": f"Bearer {user_token}"})
    assert get_resp.status_code == 404
    # Limpiar usuario creado
    from app.database import delete_user
    assert delete_user(creator["id"]) is True

def test_admin_list_games():
    """Test para verificar que el admin puede consultar todas las partidas."""
    token = get_admin_token()
    
    # Crear algunos usuarios y partidas para probar
    user1_data = {"username": "gameuser1", "email": "gameuser1@example.com", "password": "gamepass123"}
    user2_data = {"username": "gameuser2", "email": "gameuser2@example.com", "password": "gamepass123"}
    
    reg1 = client.post("/register", data=user1_data)
    reg2 = client.post("/register", data=user2_data)
    user1 = reg1.json()
    user2 = reg2.json()
    
    user1_token = get_token(user1_data["username"], user1_data["password"])
    user2_token = get_token(user2_data["username"], user2_data["password"])
    
    # Crear varias partidas
    game1_data = {
        "name": "Partida Test 1",
        "creator_id": user1["id"],
        "max_players": 6
    }
    game2_data = {
        "name": "Partida Test 2", 
        "creator_id": user2["id"],
        "max_players": 8
    }
    
    resp1 = client.post("/games", json=game1_data, headers={"Authorization": f"Bearer {user1_token}"})
    resp2 = client.post("/games", json=game2_data, headers={"Authorization": f"Bearer {user2_token}"})
    
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    
    game1 = resp1.json()
    game2 = resp2.json()
    
    # El admin debe poder ver todas las partidas
    response = client.get("/admin/games", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    games_list = response.json()
    assert isinstance(games_list, list)
    
    # Verificar que las partidas creadas están en la lista
    game_ids = [game["id"] for game in games_list]
    assert game1["id"] in game_ids
    assert game2["id"] in game_ids
    
    # Limpiar partidas y usuarios creados
    client.delete(f"/admin/games/{game1['id']}", headers={"Authorization": f"Bearer {token}"})
    client.delete(f"/admin/games/{game2['id']}", headers={"Authorization": f"Bearer {token}"})
    
    from app.database import delete_user
    assert delete_user(user1["id"]) is True
    assert delete_user(user2["id"]) is True

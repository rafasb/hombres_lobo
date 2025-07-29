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
    
    try:
        assert user["username"] == data["username"]
        assert user["email"] == data["email"]
        assert "id" in user
        assert "created_at" in user
        assert "updated_at" in user
    finally:
        # Eliminar usuario creado (siempre se ejecuta)
        delete_user(user["id"])

def test_login_and_get_user_by_id():
    data = {
        "username": "user2",
        "email": f"user2_{uuid.uuid4()}@example.com",
        "password": "pass2"
    }
    reg = client.post("/register", data=data)
    user = reg.json()
    user_id = user["id"]
    
    try:
        token = get_token(data["username"], data["password"])
        response = client.get(f"/users/{user_id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        user2 = response.json()
        assert user2["id"] == user_id
        assert user2["username"] == data["username"]
    finally:
        # Eliminar usuario creado (siempre se ejecuta)
        delete_user(user_id)

def test_list_users_auth():
    data = {
        "username": "userlist",
        "email": f"userlist_{uuid.uuid4()}@example.com",
        "password": "passlist"
    }
    reg = client.post("/register", data=data)
    user = reg.json()
    
    try:
        token = get_token(data["username"], data["password"])
        
        # Usuario regular NO debe poder acceder a lista completa de usuarios
        response = client.get("/users", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403  # Forbidden - solo admin puede ver lista completa
        
        # Pero SÍ debe poder acceder a su propio perfil
        response = client.get(f"/users/{user['id']}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["id"] == user["id"]
        
    finally:
        # Eliminar usuario creado (siempre se ejecuta)
        delete_user(user["id"])

def test_create_and_get_game_auth():
    user_data = {
        "username": "creator",
        "email": f"creator_{uuid.uuid4()}@example.com",
        "password": "creatorpass"
    }
    reg = client.post("/register", data=user_data)
    creator = reg.json()
    gid = None
    
    try:
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
        
    finally:
        # Eliminar partida creada (si se creó)
        if gid:
            delete_game(gid)
        # Eliminar usuario creador (siempre se ejecuta)
        delete_user(creator["id"])

def test_list_games_auth():
    data = {
        "username": "gamelist",
        "email": f"gamelist_{uuid.uuid4()}@example.com",
        "password": "passgamelist"
    }
    client.post("/register", data=data)
    
    try:
        token = get_token(data["username"], data["password"])
        response = client.get("/games", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    finally:
        # Eliminar usuario creado (siempre se ejecuta)
        users = load_all_users()
        user = next((u for u in users if u.username == data["username"]), None)
        if user:
            delete_user(user.id)

def test_leave_game_endpoint():
    # Crear usuario y loguear
    user_data = {
        "username": "jugador_leave",
        "email": "leave_{0}@example.com".format(uuid.uuid4()),
        "password": "leavepass"
    }
    reg = client.post("/register", data=user_data)
    user = reg.json()
    gid = None
    
    try:
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
        
    finally:
        # Limpiar datos (siempre se ejecuta)
        from app.services.game_service import delete_game
        from app.database import delete_user
        if gid:
            delete_game(gid)
        delete_user(user["id"])

def test_update_game_params_and_status_and_delete():
    # Crear usuario y loguear
    user_data = {
        "username": "creador_param",
        "email": f"param_{uuid.uuid4()}@example.com",
        "password": "parampass"
    }
    reg = client.post("/register", data=user_data)
    user = reg.json()
    gid = None
    
    try:
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
        # La partida ya fue eliminada por el endpoint
        gid = None
        
    finally:
        # Limpiar recursos (siempre se ejecuta)
        from app.database import delete_user
        if gid:  # Solo si la partida no fue eliminada por el test
            from app.services.game_service import delete_game
            delete_game(gid)
        delete_user(user["id"])

def test_get_my_profile():
    """Test para el endpoint GET /users/me - obtener perfil del usuario autenticado"""
    # Crear usuario de prueba con nombre único
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "username": f"myprofile_user_{unique_id}",
        "email": f"myprofile_{uuid.uuid4()}@example.com",
        "password": "myprofilepass123"
    }
    reg = client.post("/register", data=user_data)
    assert reg.status_code == 200
    user = reg.json()
    
    try:
        # Obtener token de autenticación
        token = get_token(user_data["username"], user_data["password"])
        
        # Hacer petición GET a /users/me
        response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        
        # Verificar respuesta exitosa
        assert response.status_code == 200
        profile = response.json()
        
        # Verificar que los datos coinciden con el usuario registrado
        assert profile["id"] == user["id"]
        assert profile["username"] == user_data["username"]
        assert profile["email"] == user_data["email"]
        assert profile["role"] == "player"
        assert profile["status"] == "active"
        assert "hashed_password" in profile
        assert "created_at" in profile
        assert "updated_at" in profile
        
    finally:
        # Limpiar usuario creado (siempre se ejecuta)
        delete_user(user["id"])

def test_get_my_profile_without_auth():
    """Test para verificar que GET /users/me requiere autenticación"""
    # Hacer petición sin token de autenticación
    response = client.get("/users/me")
    
    # Debe devolver error 401 Unauthorized
    assert response.status_code == 401

def test_get_my_profile_with_invalid_token():
    """Test para verificar que GET /users/me rechaza tokens inválidos"""
    # Hacer petición con token inválido
    response = client.get("/users/me", headers={"Authorization": "Bearer token_invalido"})
    
    # Debe devolver error 401 Unauthorized
    assert response.status_code == 401

def test_get_my_profile_with_admin_user():
    """Test para verificar que GET /users/me funciona correctamente con usuario admin"""
    # Crear usuario admin de prueba con nombre único
    unique_id = str(uuid.uuid4())[:8]
    admin_data = {
        "username": f"admin_myprofile_{unique_id}",
        "email": f"admin_myprofile_{uuid.uuid4()}@example.com", 
        "password": "adminpass123"
    }
    reg = client.post("/register", data=admin_data)
    assert reg.status_code == 200
    admin_user = reg.json()
    
    try:
        # Cambiar manualmente el rol a admin (simulando promoción)
        from app.database import load_all_users, save_user
        from app.models.user import UserRole
        users = load_all_users()
        for user in users:
            if user.id == admin_user["id"]:
                user.role = UserRole.ADMIN
                save_user(user)
                break
        
        # Obtener token de autenticación
        token = get_token(admin_data["username"], admin_data["password"])
        
        # Hacer petición GET a /users/me
        response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        
        # Verificar respuesta exitosa
        assert response.status_code == 200
        profile = response.json()
        
        # Verificar que los datos del admin son correctos
        assert profile["id"] == admin_user["id"]
        assert profile["username"] == admin_data["username"]
        assert profile["role"] == "admin"
        assert profile["status"] == "active"
        
    finally:
        # Limpiar usuario creado (siempre se ejecuta)
        delete_user(admin_user["id"])

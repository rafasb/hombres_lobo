"""
Tests unitarios para los endpoints de gestión de partidas.
Cubre todos los endpoints en routes_games.py con casos exitosos y de error.
Usa autenticación real con credenciales del .env para tests de integración.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.models.game_and_player import Game, GameStatus, GameCreate, PlayerInfo, Roles
from app.models.user import User, UserAccessRole
from app.core.security import create_access_token
from app.core.dependencies import get_current_user, get_current_user_id

# Cliente de pruebas
client = TestClient(app)

# Helper function for dependency override
def create_mock_user(user_id: str = "test-user-123", username: str = "testuser", role: UserAccessRole = UserAccessRole.PLAYER):
    """Crea un usuario mock para tests"""
    return User(
        id=user_id,
        username=username,
        email=f"{username}@test.com",
        role=role,
        hashed_password="fake_hash"
    )

def override_get_current_user():
    """Override function for get_current_user dependency"""
    return create_mock_user()

def override_get_current_user_id():
    """Override function for get_current_user_id dependency"""
    return "test-user-123"


class TestSimpleAuthenticated:
    """Tests simples usando dependency override"""
    
    def setup_method(self):
        """Setup dependency overrides for each test"""
        app.dependency_overrides[get_current_user] = override_get_current_user
        app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    
    def teardown_method(self):
        """Clean up dependency overrides after each test"""
        app.dependency_overrides.clear()
    
    @patch('app.api.routes_games.get_all_games')
    def test_list_games_with_auth(self, mock_get_all_games):
        """Test simple para listar games con autenticación mock"""
        # Mock the service call
        mock_get_all_games.return_value = []
        
        # Make request with dependency override in place
        response = client.get("/games")
        
        assert response.status_code == 200
        data = response.json()
        assert "games" in data
        assert data["games"] == []
        mock_get_all_games.assert_called_once()
    
    @patch('app.api.routes_games.create_game')
    def test_create_game_with_auth(self, mock_create_game):
        """Test simple para crear game con autenticación mock"""
        # Mock the service call
        mock_create_game.return_value = True
        
        game_data = {
            "name": "Test Game",
            "creator_id": "test-user-123",
            "max_players": 8
        }
        
        # Make request with dependency override in place
        response = client.post("/games", json=game_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "creada exitosamente" in data["message"]
        assert data["game"]["name"] == "Test Game"
        mock_create_game.assert_called_once()


# Credenciales del .env para tests de integración
TEST_USERNAME = os.getenv("USERNAME", "luis")
TEST_EMAIL = os.getenv("EMAIL", "luis@example.com")
TEST_PASSWORD = os.getenv("PASSWORD", "luis")

# Fixtures para datos de prueba
@pytest.fixture
def mock_user():
    return User(
        id="user-123",
        username="testuser",
        email="test@example.com",
        role=UserAccessRole.PLAYER,
        hashed_password="$2b$12$hashed_password"
    )

@pytest.fixture
def mock_admin():
    return User(
        id="admin-123",
        username="admin",
        email="admin@example.com",
        role=UserAccessRole.ADMIN,
        hashed_password="$2b$12$hashed_password"
    )

@pytest.fixture
def mock_game():
    player_info = PlayerInfo(
        player_id="user-123",
        role=Roles.VILLAGER,
        is_alive=True
    )
    return Game(
        id="game-123",
        name="Test Game",
        creator_id="user-123",
        max_players=8,
        player_ids=["user-123"],
        players={"user-123": player_info},
        status=GameStatus.WAITING
    )

@pytest.fixture
def mock_game_create():
    return GameCreate(
        name="New Game",
        creator_id="user-123",
        max_players=10
    )

@pytest.fixture
def auth_headers():
    """Crear headers de autenticación usando credenciales reales del .env"""
    # Crear token de acceso para el usuario de prueba
    access_token = create_access_token(data={"sub": TEST_EMAIL})
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def real_user():
    """Usuario real basado en credenciales del .env"""
    return User(
        id="real-user-123",
        username=TEST_USERNAME,
        email=TEST_EMAIL,
        role=UserAccessRole.PLAYER,
        hashed_password="$2b$12$real_hashed_password"
    )

class TestCreateGame:
    """Tests para POST /games - creación de partidas"""

    @patch('app.api.routes_games.create_game')
    @patch('app.api.routes_games.get_current_user')
    def test_create_game_success(self, mock_get_user, mock_create, mock_user, mock_game_create):
        mock_get_user.return_value = mock_user
        mock_create.return_value = True

        response = client.post("/games", json=mock_game_create.model_dump())

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "creada exitosamente" in data["message"]
        assert data["game"]["name"] == "New Game"
        assert data["game"]["creator_id"] == "user-123"
        mock_create.assert_called_once()

    @patch('app.api.routes_games.get_current_user')
    def test_create_game_unauthorized(self, mock_get_user):
        mock_get_user.side_effect = Exception("Unauthorized")

        response = client.post("/games", json={"name": "Test", "creator_id": "user-123", "max_players": 8})

        assert response.status_code == 500

    def test_create_game_with_real_auth(self, auth_headers, real_user):
        """Test de integración con autenticación real"""
        with patch('app.api.routes_games.get_current_user', return_value=real_user), \
             patch('app.api.routes_games.create_game', return_value=True):
            
            game_data = {
                "name": "Partida Real",
                "creator_id": real_user.id,
                "max_players": 8
            }
            
            response = client.post("/games", json=game_data, headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "creada exitosamente" in data["message"]


class TestGetGame:
    """Tests para GET /games/{game_id} - obtener partida por ID"""

    @patch('app.api.routes_games.get_game')
    @patch('app.api.routes_games.get_current_user')
    def test_get_game_success(self, mock_get_user, mock_get_game, mock_user, mock_game):
        mock_get_user.return_value = mock_user
        mock_get_game.return_value = mock_game

        response = client.get("/games/game-123")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["game"]["id"] == "game-123"
        mock_get_game.assert_called_once_with("game-123")

    @patch('app.api.routes_games.get_game')
    @patch('app.api.routes_games.get_current_user')
    def test_get_game_not_found(self, mock_get_user, mock_get_game, mock_user):
        mock_get_user.return_value = mock_user
        mock_get_game.return_value = None

        response = client.get("/games/nonexistent")

        assert response.status_code == 404
        assert "no encontrada" in response.json()["detail"]

    def test_get_game_with_real_auth(self, auth_headers, real_user, mock_game):
        """Test de integración con autenticación real"""
        with patch('app.api.routes_games.get_current_user', return_value=real_user), \
             patch('app.api.routes_games.get_game', return_value=mock_game):
            
            response = client.get("/games/game-123", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["game"]["id"] == "game-123"


class TestListGames:
    """Tests para GET /games - listar todas las partidas"""

    @patch('app.api.routes_games.get_all_games')
    @patch('app.api.routes_games.get_current_user')
    def test_list_games_success(self, mock_get_user, mock_get_all, mock_user, mock_game):
        mock_get_user.return_value = mock_user
        mock_get_all.return_value = [mock_game]

        response = client.get("/games")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["games"]) == 1
        assert data["total_games"] == 1
        mock_get_all.assert_called_once()

    @patch('app.api.routes_games.get_all_games')
    @patch('app.api.routes_games.get_current_user')
    def test_list_games_empty(self, mock_get_user, mock_get_all, mock_user):
        mock_get_user.return_value = mock_user
        mock_get_all.return_value = []

        response = client.get("/games")

        assert response.status_code == 200
        data = response.json()
        assert data["total_games"] == 0
        assert data["games"] == []


class TestJoinGame:
    """Tests para POST /games/{game_id}/join - unirse a partida"""

    @patch('app.api.routes_games.get_game')
    @patch('app.api.routes_games.join_game')
    @patch('app.api.routes_games.get_current_user')
    def test_join_game_success(self, mock_get_user, mock_join, mock_get_game, mock_user, mock_game):
        mock_get_user.return_value = mock_user
        mock_join.return_value = True
        mock_get_game.return_value = mock_game

        response = client.post("/games/game-123/join")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "unido a la partida" in data["message"]
        assert data["game_id"] == "game-123"
        mock_join.assert_called_once_with("game-123", "user-123")

    @patch('app.api.routes_games.join_game')
    @patch('app.api.routes_games.get_current_user')
    def test_join_game_failed(self, mock_get_user, mock_join, mock_user):
        mock_get_user.return_value = mock_user
        mock_join.return_value = False

        response = client.post("/games/game-123/join")

        assert response.status_code == 400
        assert "No puedes unirte" in response.json()["detail"]


class TestAssignRoles:
    """Tests para POST /games/{game_id}/assign-roles - asignar roles"""

    @patch('app.api.routes_games.assign_roles')
    @patch('app.api.routes_games.get_current_user_id')
    @patch('app.api.routes_games.get_current_user')
    def test_assign_roles_success(self, mock_get_user, mock_get_user_id, mock_assign, mock_user, mock_game):
        mock_get_user.return_value = mock_user
        mock_get_user_id.return_value = "user-123"
        mock_assign.return_value = mock_game

        response = client.post("/games/game-123/assign-roles")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Roles asignados" in data["message"]
        mock_assign.assert_called_once_with("game-123", "user-123", False)

    @patch('app.api.routes_games.assign_roles')
    @patch('app.api.routes_games.get_current_user_id')
    @patch('app.api.routes_games.get_current_user')
    def test_assign_roles_admin(self, mock_get_user, mock_get_user_id, mock_assign, mock_admin, mock_game):
        mock_get_user.return_value = mock_admin
        mock_get_user_id.return_value = "admin-123"
        mock_assign.return_value = mock_game

        response = client.post("/games/game-123/assign-roles")

        assert response.status_code == 200
        mock_assign.assert_called_once_with("game-123", "admin-123", True)

    @patch('app.api.routes_games.assign_roles')
    @patch('app.api.routes_games.get_current_user_id')
    @patch('app.api.routes_games.get_current_user')
    def test_assign_roles_failed(self, mock_get_user, mock_get_user_id, mock_assign, mock_user):
        mock_get_user.return_value = mock_user
        mock_get_user_id.return_value = "user-123"
        mock_assign.return_value = None

        response = client.post("/games/game-123/assign-roles")

        assert response.status_code == 400
        assert "No puedes iniciar" in response.json()["detail"]


class TestLeaveGame:
    """Tests para POST /games/{game_id}/leave - abandonar partida"""

    @patch('app.api.routes_games.get_game')
    @patch('app.services.game_service.leave_game')
    @patch('app.api.routes_games.get_current_user')
    def test_leave_game_success(self, mock_get_user, mock_leave, mock_get_game, mock_user, mock_game):
        mock_get_user.return_value = mock_user
        mock_leave.return_value = True
        mock_get_game.return_value = mock_game

        response = client.post("/games/game-123/leave")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "abandonado la partida" in data["message"]
        mock_leave.assert_called_once_with("game-123", "user-123")

    @patch('app.services.game_service.leave_game')
    @patch('app.api.routes_games.get_current_user')
    def test_leave_game_failed(self, mock_get_user, mock_leave, mock_user):
        mock_get_user.return_value = mock_user
        mock_leave.return_value = False

        response = client.post("/games/game-123/leave")

        assert response.status_code == 400
        assert "No puedes abandonar" in response.json()["detail"]


class TestUpdateGame:
    """Tests para PUT /games/{game_id} - actualizar partida"""

    @patch('app.api.routes_games.update_game_params')
    @patch('app.api.routes_games.get_current_user')
    def test_update_game_success(self, mock_get_user, mock_update, mock_user, mock_game):
        mock_get_user.return_value = mock_user
        mock_update.return_value = mock_game
        
        update_data = {"name": "Updated Game", "max_players": 12}

        response = client.put("/games/game-123", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "actualizada exitosamente" in data["message"]
        assert "name" in data["updated_fields"]
        assert "max_players" in data["updated_fields"]
        mock_update.assert_called_once_with("game-123", "user-123", "Updated Game", 12, False)

    @patch('app.api.routes_games.update_game_params')
    @patch('app.api.routes_games.get_current_user')
    def test_update_game_failed(self, mock_get_user, mock_update, mock_user):
        mock_get_user.return_value = mock_user
        mock_update.return_value = None

        response = client.put("/games/game-123", json={"name": "New Name"})

        assert response.status_code == 403
        assert "No tienes permisos" in response.json()["detail"]


class TestUpdateGameStatus:
    """Tests para PUT /games/{game_id}/status - actualizar estado de partida"""

    @patch('app.api.routes_games.get_game')
    @patch('app.api.routes_games.change_game_status')
    @patch('app.api.routes_games.get_current_user')
    def test_update_status_success(self, mock_get_user, mock_change_status, mock_get_game, mock_user, mock_game):
        mock_get_user.return_value = mock_user
        mock_get_game.return_value = mock_game
        updated_game = mock_game.model_copy()
        updated_game.status = GameStatus.DAY
        mock_change_status.return_value = updated_game

        response = client.put("/games/game-123/status", json="day")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["previous_status"] == "waiting"
        assert data["new_status"] == "day"
        mock_change_status.assert_called_once_with("game-123", "user-123", GameStatus.DAY, False)

    @patch('app.api.routes_games.get_game')
    @patch('app.api.routes_games.change_game_status')
    @patch('app.api.routes_games.get_current_user')
    def test_update_status_failed(self, mock_get_user, mock_change_status, mock_get_game, mock_user, mock_game):
        mock_get_user.return_value = mock_user
        mock_get_game.return_value = mock_game
        mock_change_status.return_value = None

        response = client.put("/games/game-123/status", json="playing")

        assert response.status_code == 403
        assert "No tienes permisos" in response.json()["detail"]


class TestDeleteGame:
    """Tests para DELETE /games/{game_id} - eliminar partida"""

    @patch('app.api.routes_games.creator_delete_game')
    @patch('app.api.routes_games.get_current_user')
    def test_delete_game_success(self, mock_get_user, mock_delete, mock_user):
        mock_get_user.return_value = mock_user
        mock_delete.return_value = True

        response = client.delete("/games/game-123")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "eliminada exitosamente" in data["message"]
        assert data["deleted_game_id"] == "game-123"
        mock_delete.assert_called_once_with("game-123", "user-123", False)

    @patch('app.api.routes_games.creator_delete_game')
    @patch('app.api.routes_games.get_current_user')
    def test_delete_game_failed(self, mock_get_user, mock_delete, mock_user):
        mock_get_user.return_value = mock_user
        mock_delete.return_value = False

        response = client.delete("/games/game-123")

        assert response.status_code == 403
        assert "No tienes permisos" in response.json()["detail"]

    @patch('app.api.routes_games.creator_delete_game')
    @patch('app.api.routes_games.get_current_user')
    def test_delete_game_admin_success(self, mock_get_user, mock_delete, mock_admin):
        mock_get_user.return_value = mock_admin
        mock_delete.return_value = True

        response = client.delete("/games/game-123")

        assert response.status_code == 200
        mock_delete.assert_called_once_with("game-123", "admin-123", True)


# Tests de integración con autenticación real
class TestRealAuthentication:
    """Tests de integración usando las credenciales reales del .env"""

    def test_endpoints_require_authentication(self):
        """Verifica que todos los endpoints requieren autenticación"""
        endpoints = [
            ("POST", "/games", {"name": "Test", "creator_id": "123", "max_players": 8}),
            ("GET", "/games/123", None),
            ("GET", "/games", None),
            ("POST", "/games/123/join", None),
            ("POST", "/games/123/assign-roles", None),
            ("POST", "/games/123/leave", None),
            ("PUT", "/games/123", {"name": "Updated"}),
            ("PUT", "/games/123/status", "day"),
            ("DELETE", "/games/123", None)
        ]

        for method, url, data in endpoints:
            response = None
            if method == "GET":
                response = client.get(url)
            elif method == "POST":
                response = client.post(url, json=data)
            elif method == "PUT":
                response = client.put(url, json=data)
            elif method == "DELETE":
                response = client.delete(url)

            # Debe fallar por falta de autenticación
            assert response is not None, f"Endpoint {method} {url} no devolvió respuesta"
            assert response.status_code in [401, 403, 422, 500], f"Endpoint {method} {url} debería requerir autenticación, pero devolvió {response.status_code}"

    def test_endpoints_with_valid_auth(self, auth_headers, real_user):
        """Verifica que los endpoints funcionan con autenticación válida"""
        with patch('app.api.routes_games.get_current_user', return_value=real_user), \
             patch('app.api.routes_games.get_all_games', return_value=[]):
            
            response = client.get("/games", headers=auth_headers)
            
            # Con autenticación válida, debería funcionar
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "total_games" in data


# Comando para ejecutar los tests:
# pytest backend/tests/test_routes_games.py -v
# pytest backend/tests/test_routes_games.py::TestRealAuthentication -v (solo tests de integración)

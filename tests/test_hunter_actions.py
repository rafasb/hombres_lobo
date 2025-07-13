"""
Tests unitarios para las acciones del Cazador durante las partidas.
Verifica el correcto funcionamiento de la habilidad de venganza cuando es eliminado.
"""

import pytest
from unittest.mock import patch
from app.models.game_and_roles import Game, GameStatus, GameRole, RoleInfo
from app.models.user import User
from app.services.player_action_service import (
    is_hunter,
    can_hunter_revenge,
    hunter_revenge_kill,
    mark_hunter_as_eliminated,
    get_hunter_revenge_targets,
    check_hunter_death_triggers,
    auto_eliminate_hunter_target,
    reset_hunter_revenge_state,
)


@pytest.fixture
def sample_game_with_hunter():
    """Fixture que crea una partida de prueba con un cazador."""
    players = [
        User(id="hunter1", username="Cazador", email="hunter@test.com", hashed_password="hash1"),
        User(id="player2", username="Aldeano", email="aldeano@test.com", hashed_password="hash2"),
        User(id="player3", username="Lobo", email="lobo@test.com", hashed_password="hash3"),
        User(id="player4", username="Vidente", email="vidente@test.com", hashed_password="hash4"),
    ]
    
    roles = {
        "hunter1": RoleInfo(
            role=GameRole.HUNTER, 
            is_alive=False,  # Cazador ya eliminado
            can_revenge_kill=True,
            has_used_revenge=False
        ),
        "player2": RoleInfo(role=GameRole.VILLAGER, is_alive=True),
        "player3": RoleInfo(role=GameRole.WAREWOLF, is_alive=True),
        "player4": RoleInfo(role=GameRole.SEER, is_alive=True),
    }
    
    return Game(
        id="test_game",
        name="Test Game",
        max_players=10,
        players=players,
        roles=roles,
        status=GameStatus.DAY,
        creator_id="hunter1"
    )


@pytest.fixture
def sample_game_with_alive_hunter():
    """Fixture que crea una partida con un cazador vivo."""
    players = [
        User(id="hunter1", username="Cazador", email="hunter@test.com", hashed_password="hash1"),
        User(id="player2", username="Aldeano", email="aldeano@test.com", hashed_password="hash2"),
        User(id="player3", username="Lobo", email="lobo@test.com", hashed_password="hash3"),
    ]
    
    roles = {
        "hunter1": RoleInfo(role=GameRole.HUNTER, is_alive=True),
        "player2": RoleInfo(role=GameRole.VILLAGER, is_alive=True),
        "player3": RoleInfo(role=GameRole.WAREWOLF, is_alive=True),
    }
    
    return Game(
        id="test_game",
        name="Test Game",
        max_players=10,
        players=players,
        roles=roles,
        status=GameStatus.DAY,
        creator_id="hunter1"
    )


@patch('app.services.player_action_service.load_game')
def test_is_hunter_success(mock_load_game, sample_game_with_hunter):
    """Test que verifica la identificación correcta del cazador."""
    mock_load_game.return_value = sample_game_with_hunter
    
    result = is_hunter("test_game", "hunter1")
    
    assert result is True
    mock_load_game.assert_called_once_with("test_game")


@patch('app.services.player_action_service.load_game')
def test_is_hunter_not_hunter(mock_load_game, sample_game_with_hunter):
    """Test que verifica que un no-cazador no se identifica como cazador."""
    mock_load_game.return_value = sample_game_with_hunter
    
    result = is_hunter("test_game", "player2")
    
    assert result is False


@patch('app.services.player_action_service.load_game')
def test_can_hunter_revenge_success(mock_load_game, sample_game_with_hunter):
    """Test que verifica que el cazador eliminado puede vengarse."""
    mock_load_game.return_value = sample_game_with_hunter
    
    result = can_hunter_revenge("test_game", "hunter1")
    
    assert result is True


@patch('app.services.player_action_service.load_game')
def test_can_hunter_revenge_alive_hunter(mock_load_game, sample_game_with_alive_hunter):
    """Test que verifica que el cazador vivo no puede vengarse."""
    mock_load_game.return_value = sample_game_with_alive_hunter
    
    result = can_hunter_revenge("test_game", "hunter1")
    
    assert result is False


@patch('app.services.player_action_service.load_game')
def test_can_hunter_revenge_already_used(mock_load_game, sample_game_with_hunter):
    """Test que verifica que el cazador no puede vengarse si ya usó su habilidad."""
    sample_game_with_hunter.roles["hunter1"].has_used_revenge = True
    mock_load_game.return_value = sample_game_with_hunter
    
    result = can_hunter_revenge("test_game", "hunter1")
    
    assert result is False


@patch('app.services.player_action_service.load_game')
@patch('app.services.player_action_service.save_game')
def test_hunter_revenge_kill_success(mock_save_game, mock_load_game, sample_game_with_hunter):
    """Test que verifica la venganza exitosa del cazador."""
    mock_load_game.return_value = sample_game_with_hunter
    mock_save_game.return_value = None
    
    result = hunter_revenge_kill("test_game", "hunter1", "player2")
    
    assert result is not None
    assert result.roles["player2"].is_alive is False  # Objetivo eliminado
    assert result.roles["hunter1"].has_used_revenge is True  # Venganza usada
    assert result.roles["hunter1"].target_player_id == "player2"
    mock_save_game.assert_called_once()


@patch('app.services.player_action_service.load_game')
def test_hunter_revenge_kill_self_target(mock_load_game, sample_game_with_hunter):
    """Test que verifica que el cazador no puede vengarse de sí mismo."""
    mock_load_game.return_value = sample_game_with_hunter
    
    result = hunter_revenge_kill("test_game", "hunter1", "hunter1")
    
    assert result is None


@patch('app.services.player_action_service.load_game')
def test_hunter_revenge_kill_dead_target(mock_load_game, sample_game_with_hunter):
    """Test que verifica que el cazador no puede vengarse de jugadores muertos."""
    # Marcar al objetivo como muerto
    sample_game_with_hunter.roles["player2"].is_alive = False
    mock_load_game.return_value = sample_game_with_hunter
    
    result = hunter_revenge_kill("test_game", "hunter1", "player2")
    
    assert result is None


@patch('app.services.player_action_service.load_game')
@patch('app.services.player_action_service.save_game')
def test_mark_hunter_as_eliminated(mock_save_game, mock_load_game, sample_game_with_alive_hunter):
    """Test que verifica la marca del cazador como eliminado."""
    mock_load_game.return_value = sample_game_with_alive_hunter
    mock_save_game.return_value = None
    
    result = mark_hunter_as_eliminated("test_game", "hunter1", "lynching")
    
    assert result is not None
    assert result.roles["hunter1"].is_alive is False
    assert result.roles["hunter1"].can_revenge_kill is True
    assert result.roles["hunter1"].has_used_revenge is False
    mock_save_game.assert_called_once()


@patch('app.services.player_action_service.load_game')
def test_get_hunter_revenge_targets(mock_load_game, sample_game_with_hunter):
    """Test que verifica la obtención de objetivos de venganza."""
    mock_load_game.return_value = sample_game_with_hunter
    
    result = get_hunter_revenge_targets("test_game", "hunter1")
    
    assert len(result) == 3  # Todos excepto el cazador (4 jugadores - 1 cazador)
    target_ids = [target["id"] for target in result]
    assert "hunter1" not in target_ids  # El cazador no debe estar incluido
    assert "player2" in target_ids
    assert "player3" in target_ids
    assert "player4" in target_ids


@patch('app.services.player_action_service.load_game')
def test_get_hunter_revenge_targets_excludes_dead_players(mock_load_game, sample_game_with_hunter):
    """Test que verifica que los jugadores muertos no aparecen como objetivos."""
    # Marcar un jugador como muerto
    sample_game_with_hunter.roles["player2"].is_alive = False
    mock_load_game.return_value = sample_game_with_hunter
    
    result = get_hunter_revenge_targets("test_game", "hunter1")
    
    assert len(result) == 2  # Solo jugadores vivos (excluyendo cazador: 4 total - 1 cazador - 1 muerto)
    target_ids = [target["id"] for target in result]
    assert "player2" not in target_ids  # Jugador muerto no incluido
    assert "player3" in target_ids
    assert "player4" in target_ids


@patch('app.services.player_action_service.load_game')
def test_check_hunter_death_triggers(mock_load_game, sample_game_with_hunter):
    """Test que verifica la detección de cazadores que necesitan venganza."""
    mock_load_game.return_value = sample_game_with_hunter
    
    result = check_hunter_death_triggers("test_game")
    
    assert len(result) == 1
    assert "hunter1" in result


@patch('app.services.player_action_service.load_game')
def test_check_hunter_death_triggers_no_hunters(mock_load_game, sample_game_with_alive_hunter):
    """Test que verifica cuando no hay cazadores que necesiten venganza."""
    mock_load_game.return_value = sample_game_with_alive_hunter
    
    result = check_hunter_death_triggers("test_game")
    
    assert len(result) == 0


@patch('app.services.player_action_service.load_game')
def test_auto_eliminate_hunter_target(mock_load_game, sample_game_with_hunter):
    """Test que verifica la obtención de información del objetivo vengado."""
    # Configurar cazador que ya se vengó
    sample_game_with_hunter.roles["hunter1"].has_used_revenge = True
    sample_game_with_hunter.roles["hunter1"].target_player_id = "player2"
    mock_load_game.return_value = sample_game_with_hunter
    
    result = auto_eliminate_hunter_target("test_game", "hunter1")
    
    assert result is not None
    assert result["id"] == "player2"
    assert result["username"] == "Aldeano"


@patch('app.services.player_action_service.load_game')
@patch('app.services.player_action_service.save_game')
def test_reset_hunter_revenge_state(mock_save_game, mock_load_game, sample_game_with_hunter):
    """Test que verifica el reinicio del estado de venganza."""
    # Configurar cazador con estado de venganza
    sample_game_with_hunter.roles["hunter1"].can_revenge_kill = True
    sample_game_with_hunter.roles["hunter1"].has_used_revenge = True
    sample_game_with_hunter.roles["hunter1"].target_player_id = "player2"
    mock_load_game.return_value = sample_game_with_hunter
    mock_save_game.return_value = None
    
    result = reset_hunter_revenge_state("test_game", "hunter1")
    
    assert result is True
    assert sample_game_with_hunter.roles["hunter1"].can_revenge_kill is False
    assert sample_game_with_hunter.roles["hunter1"].has_used_revenge is False
    assert sample_game_with_hunter.roles["hunter1"].target_player_id is None
    mock_save_game.assert_called_once()

"""
Tests unitarios para las acciones de la Vidente durante las partidas.
Verifica el correcto funcionamiento de la habilidad de investigación nocturna.
"""

import pytest
from unittest.mock import patch
from app.models.game_and_roles import Game, GameStatus, GameRole, RoleInfo
from app.models.user import User
from app.services.player_action_service import (
    can_seer_act,
    seer_vision,
    get_seer_vision_result,
    get_seer_eligible_targets,
    reset_seer_night_actions,
)


@pytest.fixture
def sample_game_with_seer():
    """Fixture que crea una partida de prueba con una vidente."""
    players = [
        User(id="player1", username="Vidente", email="vidente@test.com", hashed_password="hash1"),
        User(id="player2", username="Aldeano", email="aldeano@test.com", hashed_password="hash2"),
        User(id="player3", username="Lobo", email="lobo@test.com", hashed_password="hash3"),
        User(id="player4", username="Bruja", email="bruja@test.com", hashed_password="hash4"),
    ]
    
    roles = {
        "player1": RoleInfo(role=GameRole.SEER, is_alive=True),
        "player2": RoleInfo(role=GameRole.VILLAGER, is_alive=True),
        "player3": RoleInfo(role=GameRole.WAREWOLF, is_alive=True),
        "player4": RoleInfo(role=GameRole.WITCH, is_alive=True),
    }
    
    return Game(
        id="test_game",
        name="Test Game",
        max_players=10,
        players=players,
        roles=roles,
        status=GameStatus.NIGHT,
        creator_id="player1"
    )


@patch('app.services.player_action_service.load_game')
def test_can_seer_act_success(mock_load_game, sample_game_with_seer):
    """Test que verifica que la vidente puede actuar correctamente."""
    mock_load_game.return_value = sample_game_with_seer
    
    result = can_seer_act("test_game", "player1")
    
    assert result is True
    mock_load_game.assert_called_once_with("test_game")


@patch('app.services.player_action_service.load_game')
def test_can_seer_act_wrong_phase(mock_load_game, sample_game_with_seer):
    """Test que verifica que la vidente no puede actuar fuera de la fase nocturna."""
    sample_game_with_seer.status = GameStatus.DAY
    mock_load_game.return_value = sample_game_with_seer
    
    result = can_seer_act("test_game", "player1")
    
    assert result is False


@patch('app.services.player_action_service.load_game')
def test_can_seer_act_already_used_vision(mock_load_game, sample_game_with_seer):
    """Test que verifica que la vidente no puede actuar si ya usó su visión."""
    sample_game_with_seer.roles["player1"].has_used_vision_tonight = True
    mock_load_game.return_value = sample_game_with_seer
    
    result = can_seer_act("test_game", "player1")
    
    assert result is False


@patch('app.services.player_action_service.load_game')
@patch('app.services.player_action_service.save_game')
def test_seer_vision_success(mock_save_game, mock_load_game, sample_game_with_seer):
    """Test que verifica el uso exitoso de la visión de la vidente."""
    mock_load_game.return_value = sample_game_with_seer
    mock_save_game.return_value = None
    
    result = seer_vision("test_game", "player1", "player2")
    
    assert result is not None
    assert result.roles["player1"].has_used_vision_tonight is True
    assert result.roles["player1"].target_player_id == "player2"
    mock_save_game.assert_called_once()


@patch('app.services.player_action_service.load_game')
def test_seer_vision_self_target(mock_load_game, sample_game_with_seer):
    """Test que verifica que la vidente no puede investigarse a sí misma."""
    mock_load_game.return_value = sample_game_with_seer
    
    result = seer_vision("test_game", "player1", "player1")
    
    assert result is None


@patch('app.services.player_action_service.load_game')
def test_get_seer_vision_result(mock_load_game, sample_game_with_seer):
    """Test que verifica la obtención del resultado de la visión."""
    mock_load_game.return_value = sample_game_with_seer
    
    result = get_seer_vision_result("test_game", "player1", "player3")
    
    assert result is not None
    assert result["role"] == "warewolf"
    assert result["username"] == "Lobo"


@patch('app.services.player_action_service.load_game')
def test_get_seer_eligible_targets(mock_load_game, sample_game_with_seer):
    """Test que verifica la obtención de objetivos válidos para la vidente."""
    mock_load_game.return_value = sample_game_with_seer
    
    result = get_seer_eligible_targets("test_game", "player1")
    
    assert len(result) == 3  # Todos excepto la vidente
    target_ids = [target["id"] for target in result]
    assert "player1" not in target_ids  # La vidente no debe estar incluida
    assert "player2" in target_ids
    assert "player3" in target_ids
    assert "player4" in target_ids


@patch('app.services.player_action_service.load_game')
@patch('app.services.player_action_service.save_game')
def test_reset_seer_night_actions(mock_save_game, mock_load_game, sample_game_with_seer):
    """Test que verifica el reinicio de las acciones nocturnas de la vidente."""
    # Configurar estado inicial: vidente ya actuó
    sample_game_with_seer.roles["player1"].has_used_vision_tonight = True
    sample_game_with_seer.roles["player1"].target_player_id = "player2"
    mock_load_game.return_value = sample_game_with_seer
    mock_save_game.return_value = None
    
    result = reset_seer_night_actions("test_game")
    
    assert result is True
    assert sample_game_with_seer.roles["player1"].has_used_vision_tonight is False
    assert sample_game_with_seer.roles["player1"].target_player_id is None
    mock_save_game.assert_called_once()


@patch('app.services.player_action_service.load_game')
def test_get_seer_eligible_targets_excludes_dead_players(mock_load_game, sample_game_with_seer):
    """Test que verifica que los jugadores muertos no aparecen como objetivos válidos."""
    # Marcar un jugador como muerto
    sample_game_with_seer.roles["player2"].is_alive = False
    mock_load_game.return_value = sample_game_with_seer
    
    result = get_seer_eligible_targets("test_game", "player1")
    
    assert len(result) == 2  # Solo jugadores vivos (excluyendo la vidente)
    target_ids = [target["id"] for target in result]
    assert "player2" not in target_ids  # Jugador muerto no incluido
    assert "player3" in target_ids
    assert "player4" in target_ids

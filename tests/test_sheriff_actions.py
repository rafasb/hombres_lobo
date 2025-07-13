"""
Tests unitarios para las acciones del Alguacil durante las partidas.
Verifica el correcto funcionamiento de desempate de votaciones y elección de sucesor.
"""

import pytest
from unittest.mock import patch
from app.models.game import Game, GameStatus
from app.models.user import User
from app.models.roles import GameRole, RoleInfo
from app.services.player_action_service import (
    is_sheriff,
    can_sheriff_break_tie,
    has_day_vote_tie,
    sheriff_break_tie,
    get_tied_players,
    get_tied_players_info,
    can_sheriff_choose_successor,
    sheriff_choose_successor,
    get_sheriff_eligible_successors,
    promote_sheriff_successor,
)


@pytest.fixture
def sample_game_with_sheriff():
    """Fixture que crea una partida de prueba con un alguacil."""
    players = [
        User(id="sheriff1", username="Alguacil", email="sheriff@test.com", hashed_password="hash1"),
        User(id="player2", username="Aldeano", email="aldeano@test.com", hashed_password="hash2"),
        User(id="player3", username="Lobo", email="lobo@test.com", hashed_password="hash3"),
        User(id="player4", username="Vidente", email="vidente@test.com", hashed_password="hash4"),
    ]
    
    roles = {
        "sheriff1": RoleInfo(role=GameRole.SHERIFF, is_alive=True, has_double_vote=True, can_break_ties=True),
        "player2": RoleInfo(role=GameRole.VILLAGER, is_alive=True),
        "player3": RoleInfo(role=GameRole.WAREWOLF, is_alive=True),
        "player4": RoleInfo(role=GameRole.SEER, is_alive=True),
    }
    
    # Simular empate en votación: player2 y player3 tienen 1 voto cada uno
    day_votes = {
        "sheriff1": "player2",  # Alguacil vota por player2
        "player4": "player3",   # player4 vota por player3
    }
    
    return Game(
        id="test_game",
        name="Test Game",
        max_players=10,
        players=players,
        roles=roles,
        status=GameStatus.DAY,
        creator_id="sheriff1",
        day_votes=day_votes
    )


@patch('app.services.player_action_service.load_game')
def test_is_sheriff_success(mock_load_game, sample_game_with_sheriff):
    """Test que verifica la identificación correcta del alguacil."""
    mock_load_game.return_value = sample_game_with_sheriff
    
    result = is_sheriff("test_game", "sheriff1")
    
    assert result is True
    mock_load_game.assert_called_once_with("test_game")


@patch('app.services.player_action_service.load_game')
def test_is_sheriff_not_sheriff(mock_load_game, sample_game_with_sheriff):
    """Test que verifica que un no-alguacil no se identifica como alguacil."""
    mock_load_game.return_value = sample_game_with_sheriff
    
    result = is_sheriff("test_game", "player2")
    
    assert result is False


@patch('app.services.player_action_service.load_game')
def test_has_day_vote_tie_true(mock_load_game, sample_game_with_sheriff):
    """Test que verifica la detección correcta de empate en votación."""
    mock_load_game.return_value = sample_game_with_sheriff
    
    result = has_day_vote_tie("test_game")
    
    assert result is True


@patch('app.services.player_action_service.load_game')
def test_has_day_vote_tie_false(mock_load_game, sample_game_with_sheriff):
    """Test que verifica cuando no hay empate en votación."""
    # Añadir un voto extra para romper el empate
    sample_game_with_sheriff.day_votes["player3"] = "player2"  # player2 ahora tiene 2 votos
    mock_load_game.return_value = sample_game_with_sheriff
    
    result = has_day_vote_tie("test_game")
    
    assert result is False


@patch('app.services.player_action_service.load_game')
def test_can_sheriff_break_tie_success(mock_load_game, sample_game_with_sheriff):
    """Test que verifica que el alguacil puede desempatar cuando hay empate."""
    mock_load_game.return_value = sample_game_with_sheriff
    
    result = can_sheriff_break_tie("test_game", "sheriff1")
    
    assert result is True


@patch('app.services.player_action_service.load_game')
def test_can_sheriff_break_tie_wrong_phase(mock_load_game, sample_game_with_sheriff):
    """Test que verifica que el alguacil no puede desempatar fuera de la fase diurna."""
    sample_game_with_sheriff.status = GameStatus.NIGHT
    mock_load_game.return_value = sample_game_with_sheriff
    
    result = can_sheriff_break_tie("test_game", "sheriff1")
    
    assert result is False


@patch('app.services.player_action_service.load_game')
@patch('app.services.player_action_service.save_game')
def test_sheriff_break_tie_success(mock_save_game, mock_load_game, sample_game_with_sheriff):
    """Test que verifica el desempate exitoso por parte del alguacil."""
    mock_load_game.return_value = sample_game_with_sheriff
    mock_save_game.return_value = None
    
    result = sheriff_break_tie("test_game", "sheriff1", "player2")
    
    assert result is not None
    assert result.roles["player2"].is_alive is False  # player2 fue eliminado
    assert len(result.day_votes) == 0  # Votos limpiados
    mock_save_game.assert_called_once()


@patch('app.services.player_action_service.load_game')
def test_get_tied_players(mock_load_game, sample_game_with_sheriff):
    """Test que verifica la obtención de jugadores empatados."""
    mock_load_game.return_value = sample_game_with_sheriff
    
    result = get_tied_players("test_game")
    
    assert len(result) == 2
    assert "player2" in result
    assert "player3" in result


@patch('app.services.player_action_service.load_game')
def test_get_tied_players_info(mock_load_game, sample_game_with_sheriff):
    """Test que verifica la obtención de información de jugadores empatados."""
    mock_load_game.return_value = sample_game_with_sheriff
    
    result = get_tied_players_info("test_game")
    
    assert len(result) == 2
    player_ids = [player["id"] for player in result]
    assert "player2" in player_ids
    assert "player3" in player_ids


@patch('app.services.player_action_service.load_game')
def test_can_sheriff_choose_successor_success(mock_load_game, sample_game_with_sheriff):
    """Test que verifica que el alguacil puede elegir sucesor."""
    mock_load_game.return_value = sample_game_with_sheriff
    
    result = can_sheriff_choose_successor("test_game", "sheriff1")
    
    assert result is True


@patch('app.services.player_action_service.load_game')
@patch('app.services.player_action_service.save_game')
def test_sheriff_choose_successor_success(mock_save_game, mock_load_game, sample_game_with_sheriff):
    """Test que verifica la elección exitosa de sucesor."""
    mock_load_game.return_value = sample_game_with_sheriff
    mock_save_game.return_value = None
    
    result = sheriff_choose_successor("test_game", "sheriff1", "player2")
    
    assert result is not None
    assert result.roles["sheriff1"].successor_id == "player2"
    mock_save_game.assert_called_once()


@patch('app.services.player_action_service.load_game')
def test_sheriff_choose_successor_self_selection(mock_load_game, sample_game_with_sheriff):
    """Test que verifica que el alguacil no puede elegirse a sí mismo como sucesor."""
    mock_load_game.return_value = sample_game_with_sheriff
    
    result = sheriff_choose_successor("test_game", "sheriff1", "sheriff1")
    
    assert result is None


@patch('app.services.player_action_service.load_game')
def test_get_sheriff_eligible_successors(mock_load_game, sample_game_with_sheriff):
    """Test que verifica la obtención de candidatos a sucesor."""
    mock_load_game.return_value = sample_game_with_sheriff
    
    result = get_sheriff_eligible_successors("test_game", "sheriff1")
    
    assert len(result) == 3  # Todos excepto el alguacil
    successor_ids = [successor["id"] for successor in result]
    assert "sheriff1" not in successor_ids  # El alguacil no debe estar incluido
    assert "player2" in successor_ids
    assert "player3" in successor_ids
    assert "player4" in successor_ids


@patch('app.services.player_action_service.load_game')
@patch('app.services.player_action_service.save_game')
def test_promote_sheriff_successor(mock_save_game, mock_load_game, sample_game_with_sheriff):
    """Test que verifica la promoción del sucesor cuando el alguacil muere."""
    # Configurar sucesor
    sample_game_with_sheriff.roles["sheriff1"].successor_id = "player2"
    sample_game_with_sheriff.roles["sheriff1"].is_alive = False
    mock_load_game.return_value = sample_game_with_sheriff
    mock_save_game.return_value = None
    
    result = promote_sheriff_successor("test_game", "sheriff1")
    
    assert result is not None
    assert result.roles["player2"].role == GameRole.SHERIFF
    assert result.roles["player2"].has_double_vote is True
    assert result.roles["player2"].can_break_ties is True
    mock_save_game.assert_called_once()


@patch('app.services.player_action_service.load_game')
def test_get_sheriff_eligible_successors_excludes_dead_players(mock_load_game, sample_game_with_sheriff):
    """Test que verifica que los jugadores muertos no aparecen como candidatos a sucesor."""
    # Marcar un jugador como muerto
    sample_game_with_sheriff.roles["player2"].is_alive = False
    mock_load_game.return_value = sample_game_with_sheriff
    
    result = get_sheriff_eligible_successors("test_game", "sheriff1")
    
    assert len(result) == 2  # Solo jugadores vivos (excluyendo al alguacil)
    successor_ids = [successor["id"] for successor in result]
    assert "player2" not in successor_ids  # Jugador muerto no incluido
    assert "player3" in successor_ids
    assert "player4" in successor_ids

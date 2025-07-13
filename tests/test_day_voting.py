"""
Tests para la votación diurna de los jugadores.
Prueba específicamente la funcionalidad de votación durante la fase de día.
"""

from app.services.player_action_service import (
    day_vote,
    get_day_vote_counts,
    can_player_vote,
    get_voting_eligible_players,
    get_voting_summary,
    reset_day_votes,
)
from app.models.game import Game, GameStatus
from app.models.user import User
from app.models.roles import GameRole, RoleInfo
from app.database import save_game


def test_day_vote_success():
    """Test que un jugador puede votar exitosamente durante el día."""
    # Crear usuarios de prueba
    player1 = User(
        id="player1",
        username="jugador1",
        email="player1@test.com",
        hashed_password="hashed"
    )
    
    player2 = User(
        id="player2",
        username="jugador2",
        email="player2@test.com",
        hashed_password="hashed"
    )
    
    # Crear partida de prueba
    game = Game(
        id="test_day_vote",
        name="Test Day Vote",
        creator_id="player1",
        max_players=10,
        players=[player1, player2],
        status=GameStatus.DAY,
        roles={
            "player1": RoleInfo(role=GameRole.VILLAGER, is_alive=True),
            "player2": RoleInfo(role=GameRole.WAREWOLF, is_alive=True)
        },
        day_votes={}
    )
    
    # Guardar la partida
    save_game(game)
    
    # Ejecutar voto
    result = day_vote("test_day_vote", "player1", "player2")
    
    # Verificar que el voto fue exitoso
    assert result is not None
    assert result.day_votes["player1"] == "player2"


def test_day_vote_wrong_phase():
    """Test que no se puede votar durante la noche."""
    # Crear usuarios de prueba
    player1 = User(
        id="player1",
        username="jugador1", 
        email="player1@test.com",
        hashed_password="hashed"
    )
    
    player2 = User(
        id="player2",
        username="jugador2",
        email="player2@test.com",
        hashed_password="hashed"
    )
    
    # Crear partida de prueba en fase nocturna
    game = Game(
        id="test_day_vote_night",
        name="Test Day Vote Night",
        creator_id="player1",
        max_players=10,
        players=[player1, player2],
        status=GameStatus.NIGHT,  # Fase nocturna
        roles={
            "player1": RoleInfo(role=GameRole.VILLAGER, is_alive=True),
            "player2": RoleInfo(role=GameRole.WAREWOLF, is_alive=True)
        },
        day_votes={}
    )
    
    # Guardar la partida
    save_game(game)
    
    # Intentar votar durante la noche
    result = day_vote("test_day_vote_night", "player1", "player2")
    
    # Verificar que el voto falló
    assert result is None


def test_day_vote_self_vote():
    """Test que no se puede votar por uno mismo."""
    # Crear usuarios de prueba
    player1 = User(
        id="player1",
        username="jugador1",
        email="player1@test.com", 
        hashed_password="hashed"
    )
    
    # Crear partida de prueba
    game = Game(
        id="test_self_vote",
        name="Test Self Vote",
        creator_id="player1",
        max_players=10,
        players=[player1],
        status=GameStatus.DAY,
        roles={
            "player1": RoleInfo(role=GameRole.VILLAGER, is_alive=True)
        },
        day_votes={}
    )
    
    # Guardar la partida
    save_game(game)
    
    # Intentar votar por uno mismo
    result = day_vote("test_self_vote", "player1", "player1")
    
    # Verificar que el voto falló
    assert result is None


def test_get_day_vote_counts():
    """Test del recuento de votos diurnos."""
    # Crear usuarios de prueba
    player1 = User(id="player1", username="jugador1", email="p1@test.com", hashed_password="hashed")
    player2 = User(id="player2", username="jugador2", email="p2@test.com", hashed_password="hashed")
    player3 = User(id="player3", username="jugador3", email="p3@test.com", hashed_password="hashed")
    
    # Crear partida de prueba
    game = Game(
        id="test_vote_counts",
        name="Test Vote Counts",
        creator_id="player1",
        max_players=10,
        players=[player1, player2, player3],
        status=GameStatus.DAY,
        roles={
            "player1": RoleInfo(role=GameRole.VILLAGER, is_alive=True),
            "player2": RoleInfo(role=GameRole.VILLAGER, is_alive=True),
            "player3": RoleInfo(role=GameRole.WAREWOLF, is_alive=True)
        },
        day_votes={"player1": "player3", "player2": "player3"}  # Ambos votan por player3
    )
    
    # Guardar la partida
    save_game(game)
    
    # Obtener recuento de votos
    vote_counts = get_day_vote_counts("test_vote_counts")
    
    # Verificar recuentos
    player3_votes = next((v for v in vote_counts if v["player_id"] == "player3"), None)
    assert player3_votes is not None
    assert player3_votes["vote_count"] == 2
    
    player1_votes = next((v for v in vote_counts if v["player_id"] == "player1"), None)
    assert player1_votes is not None
    assert player1_votes["vote_count"] == 0


def test_can_player_vote():
    """Test que verifica correctamente si un jugador puede votar."""
    # Crear usuarios de prueba
    alive_player = User(
        id="alive1",
        username="vivo1",
        email="alive1@test.com",
        hashed_password="hashed"
    )
    
    dead_player = User(
        id="dead1", 
        username="muerto1",
        email="dead1@test.com",
        hashed_password="hashed"
    )
    
    # Crear partida de prueba
    game = Game(
        id="test_can_vote",
        name="Test Can Vote",
        creator_id="alive1",
        max_players=10,
        players=[alive_player, dead_player],
        status=GameStatus.DAY,
        roles={
            "alive1": RoleInfo(role=GameRole.VILLAGER, is_alive=True),
            "dead1": RoleInfo(role=GameRole.VILLAGER, is_alive=False)  # Jugador muerto
        },
        day_votes={}
    )
    
    # Guardar la partida
    save_game(game)
    
    # Verificar permisos de voto
    assert can_player_vote("test_can_vote", "alive1") is True  # Jugador vivo puede votar
    assert can_player_vote("test_can_vote", "dead1") is False  # Jugador muerto no puede votar


def test_get_voting_eligible_players():
    """Test que obtiene correctamente los jugadores elegibles para votación."""
    # Crear usuarios de prueba
    player1 = User(id="player1", username="jugador1", email="p1@test.com", hashed_password="hashed")
    player2 = User(id="player2", username="jugador2", email="p2@test.com", hashed_password="hashed")
    player3 = User(id="player3", username="jugador3", email="p3@test.com", hashed_password="hashed")
    
    # Crear partida de prueba
    game = Game(
        id="test_eligible_players",
        name="Test Eligible Players",
        creator_id="player1",
        max_players=10,
        players=[player1, player2, player3],
        status=GameStatus.DAY,
        roles={
            "player1": RoleInfo(role=GameRole.VILLAGER, is_alive=True),
            "player2": RoleInfo(role=GameRole.WAREWOLF, is_alive=True),
            "player3": RoleInfo(role=GameRole.VILLAGER, is_alive=False)  # Muerto
        },
        day_votes={}
    )
    
    # Guardar la partida
    save_game(game)
    
    # Obtener jugadores elegibles
    eligible = get_voting_eligible_players("test_eligible_players")
    
    # Verificar que solo devuelve jugadores vivos
    assert len(eligible) == 2
    eligible_ids = [player["id"] for player in eligible]
    assert "player1" in eligible_ids
    assert "player2" in eligible_ids
    assert "player3" not in eligible_ids  # Jugador muerto no debe estar


def test_get_voting_summary():
    """Test del resumen completo de votación."""
    # Crear usuarios de prueba
    player1 = User(id="player1", username="jugador1", email="p1@test.com", hashed_password="hashed")
    player2 = User(id="player2", username="jugador2", email="p2@test.com", hashed_password="hashed")
    player3 = User(id="player3", username="jugador3", email="p3@test.com", hashed_password="hashed")
    
    # Crear partida de prueba
    game = Game(
        id="test_voting_summary",
        name="Test Voting Summary",
        creator_id="player1",
        max_players=10,
        players=[player1, player2, player3],
        status=GameStatus.DAY,
        roles={
            "player1": RoleInfo(role=GameRole.VILLAGER, is_alive=True),
            "player2": RoleInfo(role=GameRole.VILLAGER, is_alive=True),
            "player3": RoleInfo(role=GameRole.WAREWOLF, is_alive=True)
        },
        day_votes={"player1": "player3"}  # Solo player1 ha votado
    )
    
    # Guardar la partida
    save_game(game)
    
    # Obtener resumen
    summary = get_voting_summary("test_voting_summary")
    
    # Verificar resumen
    assert summary["total_players"] == 3
    assert summary["total_votes"] == 1
    assert summary["voting_complete"] is False  # No todos han votado
    assert summary["game_status"] == "day"


def test_reset_day_votes():
    """Test que reinicia correctamente los votos diurnos."""
    # Crear usuarios de prueba
    player1 = User(id="player1", username="jugador1", email="p1@test.com", hashed_password="hashed")
    player2 = User(id="player2", username="jugador2", email="p2@test.com", hashed_password="hashed")
    
    # Crear partida con votos existentes
    game = Game(
        id="test_reset_votes",
        name="Test Reset Votes",
        creator_id="player1",
        max_players=10,
        players=[player1, player2],
        status=GameStatus.DAY,
        roles={
            "player1": RoleInfo(role=GameRole.VILLAGER, is_alive=True),
            "player2": RoleInfo(role=GameRole.WAREWOLF, is_alive=True)
        },
        day_votes={"player1": "player2"}  # Voto existente
    )
    
    # Guardar la partida
    save_game(game)
    
    # Reiniciar votos
    result = reset_day_votes("test_reset_votes")
    
    # Verificar que se reiniciaron
    assert result is not None
    assert len(result.day_votes) == 0

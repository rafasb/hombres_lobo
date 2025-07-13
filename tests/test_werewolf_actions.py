"""
Tests para las acciones de los jugadores durante las partidas.
Prueba específicamente la funcionalidad de ataque de los hombres lobo.
"""

from app.services.player_action_service import (
    werewolf_attack,
    get_werewolf_attack_consensus,
    get_non_werewolf_players,
    can_werewolf_act,
)
from app.models.game import Game, GameStatus
from app.models.user import User
from app.models.roles import GameRole, RoleInfo
from app.database import save_game


def test_werewolf_attack_success():
    """Test que un hombre lobo puede atacar exitosamente a un aldeano."""
    # Crear usuarios de prueba
    werewolf_user = User(
        id="werewolf1",
        username="werewolf_player",
        email="werewolf@test.com",
        hashed_password="hashed"
    )
    
    villager_user = User(
        id="villager1",
        username="villager_player",
        email="villager@test.com",
        hashed_password="hashed"
    )
    
    # Crear partida de prueba
    game = Game(
        id="test_game",
        name="Test Game",
        creator_id="werewolf1",
        max_players=10,
        players=[werewolf_user, villager_user],
        status=GameStatus.NIGHT,
        roles={
            "werewolf1": RoleInfo(role=GameRole.WEREWOLF, is_alive=True),
            "villager1": RoleInfo(role=GameRole.VILLAGER, is_alive=True)
        },
        night_actions={}
    )
    
    # Guardar la partida
    save_game(game)
    
    # Ejecutar ataque
    result = werewolf_attack("test_game", "werewolf1", "villager1")
    
    # Verificar que el ataque fue exitoso
    assert result is not None
    assert result.roles["werewolf1"].has_acted_tonight is True
    assert result.roles["werewolf1"].target_player_id == "villager1"
    assert "werewolf_attacks" in result.night_actions
    assert result.night_actions["werewolf_attacks"]["werewolf1"] == "villager1"


def test_werewolf_attack_invalid_target():
    """Test que un hombre lobo no puede atacar a otro hombre lobo."""
    # Crear usuarios de prueba
    werewolf1 = User(
        id="werewolf1",
        username="werewolf1",
        email="werewolf1@test.com",
        hashed_password="hashed"
    )
    
    werewolf2 = User(
        id="werewolf2",
        username="werewolf2",
        email="werewolf2@test.com",
        hashed_password="hashed"
    )
    
    # Crear partida de prueba
    game = Game(
        id="test_game2",
        name="Test Game 2",
        creator_id="werewolf1",
        max_players=10,
        players=[werewolf1, werewolf2],
        status=GameStatus.NIGHT,
        roles={
            "werewolf1": RoleInfo(role=GameRole.WEREWOLF, is_alive=True),
            "werewolf2": RoleInfo(role=GameRole.WEREWOLF, is_alive=True)
        },
        night_actions={}
    )
    
    # Guardar la partida
    save_game(game)
    
    # Intentar ataque inválido
    result = werewolf_attack("test_game2", "werewolf1", "werewolf2")
    
    # Verificar que el ataque falló
    assert result is None


def test_werewolf_attack_wrong_phase():
    """Test que los hombres lobo no pueden atacar durante el día."""
    # Crear usuarios de prueba
    werewolf_user = User(
        id="werewolf1",
        username="werewolf_player",
        email="werewolf@test.com",
        hashed_password="hashed"
    )
    
    villager_user = User(
        id="villager1",
        username="villager_player",
        email="villager@test.com",
        hashed_password="hashed"
    )
    
    # Crear partida de prueba en fase de día
    game = Game(
        id="test_game3",
        name="Test Game 3",
        creator_id="werewolf1",
        max_players=10,
        players=[werewolf_user, villager_user],
        status=GameStatus.DAY,  # Fase de día
        roles={
            "werewolf1": RoleInfo(role=GameRole.WEREWOLF, is_alive=True),
            "villager1": RoleInfo(role=GameRole.VILLAGER, is_alive=True)
        },
        night_actions={}
    )
    
    # Guardar la partida
    save_game(game)
    
    # Intentar ataque durante el día
    result = werewolf_attack("test_game3", "werewolf1", "villager1")
    
    # Verificar que el ataque falló
    assert result is None


def test_werewolf_consensus():
    """Test del consenso entre múltiples hombres lobo."""
    # Crear usuarios de prueba
    werewolf1 = User(id="werewolf1", username="werewolf1", email="w1@test.com", hashed_password="hashed")
    werewolf2 = User(id="werewolf2", username="werewolf2", email="w2@test.com", hashed_password="hashed")
    villager1 = User(id="villager1", username="villager1", email="v1@test.com", hashed_password="hashed")
    villager2 = User(id="villager2", username="villager2", email="v2@test.com", hashed_password="hashed")
    
    # Crear partida de prueba
    game = Game(
        id="test_game4",
        name="Test Game 4",
        creator_id="werewolf1",
        max_players=10,
        players=[werewolf1, werewolf2, villager1, villager2],
        status=GameStatus.NIGHT,
        roles={
            "werewolf1": RoleInfo(role=GameRole.WEREWOLF, is_alive=True),
            "werewolf2": RoleInfo(role=GameRole.WEREWOLF, is_alive=True),
            "villager1": RoleInfo(role=GameRole.VILLAGER, is_alive=True),
            "villager2": RoleInfo(role=GameRole.VILLAGER, is_alive=True)
        },
        night_actions={}
    )
    
    # Guardar la partida
    save_game(game)
    
    # Ambos hombres lobo votan por el mismo objetivo
    werewolf_attack("test_game4", "werewolf1", "villager1")
    werewolf_attack("test_game4", "werewolf2", "villager1")
    
    # Verificar consenso
    consensus = get_werewolf_attack_consensus("test_game4")
    assert consensus == "villager1"


def test_get_non_werewolf_players():
    """Test que obtiene correctamente los jugadores que no son hombres lobo."""
    # Crear usuarios de prueba
    werewolf1 = User(id="werewolf1", username="werewolf1", email="w1@test.com", hashed_password="hashed")
    villager1 = User(id="villager1", username="villager1", email="v1@test.com", hashed_password="hashed")
    seer1 = User(id="seer1", username="seer1", email="s1@test.com", hashed_password="hashed")
    
    # Crear partida de prueba
    game = Game(
        id="test_game5",
        name="Test Game 5",
        creator_id="werewolf1",
        max_players=10,
        players=[werewolf1, villager1, seer1],
        status=GameStatus.NIGHT,
        roles={
            "werewolf1": RoleInfo(role=GameRole.WEREWOLF, is_alive=True),
            "villager1": RoleInfo(role=GameRole.VILLAGER, is_alive=True),
            "seer1": RoleInfo(role=GameRole.SEER, is_alive=True)
        },
        night_actions={}
    )
    
    # Guardar la partida
    save_game(game)
    
    # Obtener objetivos válidos
    targets = get_non_werewolf_players("test_game5")
    
    # Verificar que solo devuelve no-hombres lobo
    assert len(targets) == 2
    target_ids = [target["id"] for target in targets]
    assert "villager1" in target_ids
    assert "seer1" in target_ids
    assert "werewolf1" not in target_ids


def test_can_werewolf_act():
    """Test que verifica correctamente si un hombre lobo puede actuar."""
    # Crear usuarios de prueba
    werewolf_user = User(
        id="werewolf1",
        username="werewolf_player",
        email="werewolf@test.com",
        hashed_password="hashed"
    )
    
    villager_user = User(
        id="villager1",
        username="villager_player",
        email="villager@test.com",
        hashed_password="hashed"
    )
    
    # Crear partida de prueba
    game = Game(
        id="test_game6",
        name="Test Game 6",
        creator_id="werewolf1",
        max_players=10,
        players=[werewolf_user, villager_user],
        status=GameStatus.NIGHT,
        roles={
            "werewolf1": RoleInfo(role=GameRole.WEREWOLF, is_alive=True),
            "villager1": RoleInfo(role=GameRole.VILLAGER, is_alive=True)
        },
        night_actions={}
    )
    
    # Guardar la partida
    save_game(game)
    
    # Verificar que puede actuar inicialmente
    assert can_werewolf_act("test_game6", "werewolf1") is True
    
    # Verificar que el aldeano no puede actuar como hombre lobo
    assert can_werewolf_act("test_game6", "villager1") is False
    
    # Después de actuar, no debería poder actuar de nuevo
    werewolf_attack("test_game6", "werewolf1", "villager1")
    assert can_werewolf_act("test_game6", "werewolf1") is False

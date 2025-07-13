"""
Tests para las acciones de los jugadores durante las partidas.
Prueba específicamente la funcionalidad de ataque de los hombres lobo.
"""

from app.services.player_warewolf_action_service import (
    warewolf_attack,
    get_warewolf_attack_consensus,
    get_non_warewolf_players,
    can_warewolf_act,
)
from app.models.game_and_roles import Game, GameStatus, GameRole, RoleInfo
from app.models.user import User
from app.database import save_game


def test_warewolf_attack_success():
    """Test que un hombre lobo puede atacar exitosamente a un aldeano."""
    # Crear usuarios de prueba
    warewolf_user = User(
        id="warewolf1",
        username="warewolf_player",
        email="warewolf@test.com",
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
        creator_id="warewolf1",
        max_players=10,
        players=[warewolf_user, villager_user],
        status=GameStatus.NIGHT,
        roles={
            "warewolf1": RoleInfo(role=GameRole.WAREWOLF, is_alive=True),
            "villager1": RoleInfo(role=GameRole.VILLAGER, is_alive=True)
        },
        night_actions={}
    )
    
    # Guardar la partida
    save_game(game)
    
    # Ejecutar ataque
    result = warewolf_attack("test_game", "warewolf1", "villager1")
    
    # Verificar que el ataque fue exitoso
    assert result is not None
    assert result.roles["warewolf1"].has_acted_tonight is True
    assert result.roles["warewolf1"].target_player_id == "villager1"
    assert "warewolf_attacks" in result.night_actions
    assert result.night_actions["warewolf_attacks"]["warewolf1"] == "villager1"


def test_warewolf_attack_invalid_target():
    """Test que un hombre lobo no puede atacar a otro hombre lobo."""
    # Crear usuarios de prueba
    warewolf1 = User(
        id="warewolf1",
        username="warewolf1",
        email="warewolf1@test.com",
        hashed_password="hashed"
    )
    
    warewolf2 = User(
        id="warewolf2",
        username="warewolf2",
        email="warewolf2@test.com",
        hashed_password="hashed"
    )
    
    # Crear partida de prueba
    game = Game(
        id="test_game2",
        name="Test Game 2",
        creator_id="warewolf1",
        max_players=10,
        players=[warewolf1, warewolf2],
        status=GameStatus.NIGHT,
        roles={
            "warewolf1": RoleInfo(role=GameRole.WAREWOLF, is_alive=True),
            "warewolf2": RoleInfo(role=GameRole.WAREWOLF, is_alive=True)
        },
        night_actions={}
    )
    
    # Guardar la partida
    save_game(game)
    
    # Intentar ataque inválido
    result = warewolf_attack("test_game2", "warewolf1", "warewolf2")
    
    # Verificar que el ataque falló
    assert result is None


def test_warewolf_attack_wrong_phase():
    """Test que los hombres lobo no pueden atacar durante el día."""
    # Crear usuarios de prueba
    warewolf_user = User(
        id="warewolf1",
        username="warewolf_player",
        email="warewolf@test.com",
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
        creator_id="warewolf1",
        max_players=10,
        players=[warewolf_user, villager_user],
        status=GameStatus.DAY,  # Fase de día
        roles={
            "warewolf1": RoleInfo(role=GameRole.WAREWOLF, is_alive=True),
            "villager1": RoleInfo(role=GameRole.VILLAGER, is_alive=True)
        },
        night_actions={}
    )
    
    # Guardar la partida
    save_game(game)
    
    # Intentar ataque durante el día
    result = warewolf_attack("test_game3", "warewolf1", "villager1")
    
    # Verificar que el ataque falló
    assert result is None


def test_warewolf_consensus():
    """Test del consenso entre múltiples hombres lobo."""
    # Crear usuarios de prueba
    warewolf1 = User(id="warewolf1", username="warewolf1", email="w1@test.com", hashed_password="hashed")
    warewolf2 = User(id="warewolf2", username="warewolf2", email="w2@test.com", hashed_password="hashed")
    villager1 = User(id="villager1", username="villager1", email="v1@test.com", hashed_password="hashed")
    villager2 = User(id="villager2", username="villager2", email="v2@test.com", hashed_password="hashed")
    
    # Crear partida de prueba
    game = Game(
        id="test_game4",
        name="Test Game 4",
        creator_id="warewolf1",
        max_players=10,
        players=[warewolf1, warewolf2, villager1, villager2],
        status=GameStatus.NIGHT,
        roles={
            "warewolf1": RoleInfo(role=GameRole.WAREWOLF, is_alive=True),
            "warewolf2": RoleInfo(role=GameRole.WAREWOLF, is_alive=True),
            "villager1": RoleInfo(role=GameRole.VILLAGER, is_alive=True),
            "villager2": RoleInfo(role=GameRole.VILLAGER, is_alive=True)
        },
        night_actions={}
    )
    
    # Guardar la partida
    save_game(game)
    
    # Ambos hombres lobo votan por el mismo objetivo
    warewolf_attack("test_game4", "warewolf1", "villager1")
    warewolf_attack("test_game4", "warewolf2", "villager1")
    
    # Verificar consenso
    consensus = get_warewolf_attack_consensus("test_game4")
    assert consensus == "villager1"


def test_get_non_warewolf_players():
    """Test que obtiene correctamente los jugadores que no son hombres lobo."""
    # Crear usuarios de prueba
    warewolf1 = User(id="warewolf1", username="warewolf1", email="w1@test.com", hashed_password="hashed")
    villager1 = User(id="villager1", username="villager1", email="v1@test.com", hashed_password="hashed")
    seer1 = User(id="seer1", username="seer1", email="s1@test.com", hashed_password="hashed")
    
    # Crear partida de prueba
    game = Game(
        id="test_game5",
        name="Test Game 5",
        creator_id="warewolf1",
        max_players=10,
        players=[warewolf1, villager1, seer1],
        status=GameStatus.NIGHT,
        roles={
            "warewolf1": RoleInfo(role=GameRole.WAREWOLF, is_alive=True),
            "villager1": RoleInfo(role=GameRole.VILLAGER, is_alive=True),
            "seer1": RoleInfo(role=GameRole.SEER, is_alive=True)
        },
        night_actions={}
    )
    
    # Guardar la partida
    save_game(game)
    
    # Obtener objetivos válidos
    targets = get_non_warewolf_players("test_game5")
    
    # Verificar que solo devuelve no-hombres lobo
    assert len(targets) == 2
    target_ids = [target["id"] for target in targets]
    assert "villager1" in target_ids
    assert "seer1" in target_ids
    assert "warewolf1" not in target_ids


def test_can_warewolf_act():
    """Test que verifica correctamente si un hombre lobo puede actuar."""
    # Crear usuarios de prueba
    warewolf_user = User(
        id="warewolf1",
        username="warewolf_player",
        email="warewolf@test.com",
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
        creator_id="warewolf1",
        max_players=10,
        players=[warewolf_user, villager_user],
        status=GameStatus.NIGHT,
        roles={
            "warewolf1": RoleInfo(role=GameRole.WAREWOLF, is_alive=True),
            "villager1": RoleInfo(role=GameRole.VILLAGER, is_alive=True)
        },
        night_actions={}
    )
    
    # Guardar la partida
    save_game(game)
    
    # Verificar que puede actuar inicialmente
    assert can_warewolf_act("test_game6", "warewolf1") is True
    
    # Verificar que el aldeano no puede actuar como hombre lobo
    assert can_warewolf_act("test_game6", "villager1") is False
    
    # Después de actuar, no debería poder actuar de nuevo
    warewolf_attack("test_game6", "warewolf1", "villager1")
    assert can_warewolf_act("test_game6", "warewolf1") is False

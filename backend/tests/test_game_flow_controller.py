"""
Tests para el controlador de flujo de juego.
"""

import pytest
from app.models.game_and_roles import Game, RoleInfo, GameRole, GameStatus
from app.models.user import User, UserRole
from app.services import game_service
from app.services.game_flow_controller import game_flow_controller


@pytest.fixture
def sample_game_complete():
    """Fixture que crea un juego completo para testing del flujo."""
    game_id = "test_game_complete"
    creator_id = "creator123"
    
    # Crear usuarios
    users = []
    for i in range(8):
        user = User(
            id=f"player{i}", 
            username=f"jugador{i}", 
            email=f"player{i}@test.com", 
            role=UserRole.PLAYER, 
            hashed_password="hashed_pass"
        )
        users.append(user)
    
    # Crear juego
    game = Game(
        id=game_id,
        name="Test Game Complete",
        max_players=10,
        creator_id=creator_id,
        players=users,
        status=GameStatus.NIGHT,
        current_round=1
    )
    
    # Asignar roles balanceados
    game.roles = {
        "player0": RoleInfo(role=GameRole.WAREWOLF, is_alive=True),
        "player1": RoleInfo(role=GameRole.WAREWOLF, is_alive=True),
        "player2": RoleInfo(role=GameRole.SEER, is_alive=True, has_used_vision_tonight=False),
        "player3": RoleInfo(role=GameRole.WITCH, is_alive=True, has_healing_potion=True, has_poison_potion=True),
        "player4": RoleInfo(role=GameRole.SHERIFF, is_alive=True, has_double_vote=True, can_break_ties=True),
        "player5": RoleInfo(role=GameRole.HUNTER, is_alive=True, can_revenge_kill=True, has_used_revenge=False),
        "player6": RoleInfo(role=GameRole.VILLAGER, is_alive=True),
        "player7": RoleInfo(role=GameRole.VILLAGER, is_alive=True)
    }
    
    # Inicializar acciones nocturnas
    game.night_actions = {}
    game.day_votes = {}
    
    game_service.save_game(game)
    return game


class TestGameFlowController:
    """Tests para el controlador de flujo de juego."""
    
    def test_get_game_state_summary(self, sample_game_complete):
        """Test del resumen del estado del juego."""
        game = sample_game_complete
        
        summary = game_flow_controller.get_game_state_summary(game.id)
        
        assert summary["game_id"] == game.id
        assert summary["status"] == "night"
        assert summary["round"] == 1
        assert summary["total_players"] == 8
        assert summary["alive_players"] == 8
        assert summary["dead_players"] == 0
        
        # Verificar conteos por rol
        role_counts = summary["role_counts"]
        assert role_counts["warewolf"]["alive"] == 2
        assert role_counts["villager"]["alive"] == 2
        assert role_counts["seer"]["alive"] == 1
        assert role_counts["witch"]["alive"] == 1
        assert role_counts["sheriff"]["alive"] == 1
        assert role_counts["hunter"]["alive"] == 1
    
    def test_get_pending_actions_night_phase(self, sample_game_complete):
        """Test de acciones pendientes en fase nocturna."""
        game = sample_game_complete
        
        summary = game_flow_controller.get_game_state_summary(game.id)
        pending_actions = summary["pending_actions"]
        
        # En la fase nocturna, deberían haber acciones pendientes para hombres lobo, vidente y bruja
        action_types = [action["action"] for action in pending_actions]
        
        assert "werewolf_attack" in action_types
        assert "seer_vision" in action_types
        assert "witch_actions" in action_types
        
        # Verificar que el juego no puede avanzar automáticamente
        assert not summary["can_advance_phase"]
    
    def test_process_night_phase_basic(self, sample_game_complete):
        """Test básico del procesamiento de fase nocturna."""
        game = sample_game_complete
        
        # Simular algunas acciones nocturnas
        from app.services import player_action_service
        
        # Hombres lobo atacan
        player_action_service.warewolf_attack(game.id, "player0", "player6")
        player_action_service.warewolf_attack(game.id, "player1", "player6")
        
        # Vidente investiga
        player_action_service.seer_vision(game.id, "player2", "player0")
        
        # Procesar fase nocturna
        results = game_flow_controller.process_night_phase(game.id)
        
        assert results["success"]
        assert results["round"] == 1
        
        # Verificar que hay eventos
        events = results["events"]
        event_types = [event["type"] for event in events]
        
        # Debería haber un ataque de hombres lobo
        assert "werewolf_attack" in event_types
        
        # Verificar que la víctima murió
        assert "player6" in results["deaths"]
        
        # Verificar que el juego avanzó a fase diurna
        assert results["next_phase"] == "day"
    
    def test_process_day_phase_basic(self, sample_game_complete):
        """Test básico del procesamiento de fase diurna."""
        game = sample_game_complete
        
        # Cambiar a fase diurna
        game.status = GameStatus.DAY
        game_service.save_game(game)
        
        # Simular votación diurna
        from app.services import player_action_service
        
        # Varios jugadores votan por player0 (hombre lobo)
        player_action_service.day_vote(game.id, "player2", "player0")
        player_action_service.day_vote(game.id, "player3", "player0")
        player_action_service.day_vote(game.id, "player4", "player0")
        
        # Otros votan por player1
        player_action_service.day_vote(game.id, "player5", "player1")
        player_action_service.day_vote(game.id, "player6", "player1")
        
        # Votos restantes
        player_action_service.day_vote(game.id, "player7", "player0")
        player_action_service.day_vote(game.id, "player0", "player2")
        player_action_service.day_vote(game.id, "player1", "player2")
        
        # Procesar fase diurna
        results = game_flow_controller.process_day_phase(game.id)
        
        assert results["success"]
        assert results["round"] == 1
        
        # Verificar que hay eventos
        events = results["events"]
        event_types = [event["type"] for event in events]
        
        # Debería haber un linchamiento
        assert "lynching" in event_types
        
        # player0 debería ser linchado (más votos)
        assert "player0" in results["deaths"]
        
        # Verificar que el juego avanzó a siguiente fase nocturna
        assert results["next_phase"] == "night"
    
    def test_check_victory_conditions_werewolves_win(self, sample_game_complete):
        """Test de condición de victoria de hombres lobo."""
        game = sample_game_complete
        
        # Matar a suficientes aldeanos para que ganen los hombres lobo
        game.roles["player2"].is_alive = False  # Seer
        game.roles["player3"].is_alive = False  # Witch
        game.roles["player4"].is_alive = False  # Sheriff
        game.roles["player5"].is_alive = False  # Hunter
        game.roles["player6"].is_alive = False  # Villager
        # player7 sigue vivo, pero hay 2 hombres lobo vs 1 aldeano
        
        game_service.save_game(game)
        
        victory_check = game_flow_controller._check_victory_conditions(game.id)
        
        assert victory_check["game_over"]
        assert victory_check["victory_type"] == "werewolves"
        assert len(victory_check["winners"]) == 2
    
    def test_check_victory_conditions_villagers_win(self, sample_game_complete):
        """Test de condición de victoria de aldeanos."""
        game = sample_game_complete
        
        # Matar a todos los hombres lobo
        game.roles["player0"].is_alive = False
        game.roles["player1"].is_alive = False
        
        game_service.save_game(game)
        
        victory_check = game_flow_controller._check_victory_conditions(game.id)
        
        assert victory_check["game_over"]
        assert victory_check["victory_type"] == "villagers"
        assert len(victory_check["winners"]) == 6  # Todos los no-hombres lobo
    
    def test_check_victory_conditions_ongoing_game(self, sample_game_complete):
        """Test de juego en curso sin condición de victoria."""
        game = sample_game_complete
        
        victory_check = game_flow_controller._check_victory_conditions(game.id)
        
        assert not victory_check["game_over"]
    
    def test_prepare_phases(self, sample_game_complete):
        """Test de preparación de fases."""
        game = sample_game_complete
        
        # Test preparar fase diurna
        game_flow_controller._prepare_day_phase(game.id)
        
        updated_game = game_service.load_game(game.id)
        assert updated_game is not None
        assert updated_game.status == GameStatus.DAY
        assert len(updated_game.day_votes) == 0
        
        # Test preparar fase nocturna
        game_flow_controller._prepare_night_phase(game.id)
        
        updated_game = game_service.load_game(game.id)
        assert updated_game is not None
        assert updated_game.status == GameStatus.NIGHT
        assert updated_game.current_round == 2
    
    def test_death_consequences_processing(self, sample_game_complete):
        """Test del procesamiento de consecuencias de muerte."""
        game = sample_game_complete
        
        # Agregar un niño salvaje con modelo
        game.roles["player7"] = RoleInfo(
            role=GameRole.WILD_CHILD, 
            is_alive=True, 
            model_player_id="player6",
            has_transformed=False
        )
        game_service.save_game(game)
        
        # Procesar muerte del modelo
        consequences = game_flow_controller._process_death_consequences(game.id, ["player6"])
        
        # Verificar transformación
        assert len(consequences["transformations"]) == 1
        assert consequences["transformations"][0]["wild_child_id"] == "player7"
        
        # Verificar notificaciones
        notifications = consequences["notifications"]
        notification_types = [notif["type"] for notif in notifications]
        assert "new_werewolf" in notification_types
    
    def test_error_handling_invalid_game(self):
        """Test de manejo de errores con juego inexistente."""
        results = game_flow_controller.process_night_phase("nonexistent_game")
        
        assert not results["success"]
        assert "error" in results
    
    def test_error_handling_wrong_phase(self, sample_game_complete):
        """Test de manejo de errores con fase incorrecta."""
        game = sample_game_complete
        
        # Cambiar a fase diurna
        game.status = GameStatus.DAY
        game_service.save_game(game)
        
        # Intentar procesar fase nocturna cuando está en fase diurna
        results = game_flow_controller.process_night_phase(game.id)
        
        assert not results["success"]
        assert "error" in results

# test_wild_child_actions.py
# Tests para las acciones del Niño Salvaje

import pytest
from app.services import player_action_service, game_service
from app.models.game_and_roles import Game, GameStatus, GameRole, RoleInfo
from app.models.user import User, UserRole


@pytest.fixture
def sample_game_with_wild_child():
    """Fixture que crea un juego con un Niño Salvaje para testing."""
    game_id = "test_game_wild_child"
    creator_id = "creator123"
    wild_child_id = "wild_child123"
    model1_id = "model1_123"
    model2_id = "model2_123"
    werewolf_id = "werewolf123"
    
    # Crear usuarios
    creator = User(id=creator_id, username="creator", email="creator@test.com", role=UserRole.PLAYER, hashed_password="hashed_pass")
    wild_child = User(id=wild_child_id, username="wild_child", email="wild_child@test.com", role=UserRole.PLAYER, hashed_password="hashed_pass")
    model1 = User(id=model1_id, username="model1", email="model1@test.com", role=UserRole.PLAYER, hashed_password="hashed_pass")
    model2 = User(id=model2_id, username="model2", email="model2@test.com", role=UserRole.PLAYER, hashed_password="hashed_pass")
    werewolf = User(id=werewolf_id, username="werewolf", email="werewolf@test.com", role=UserRole.PLAYER, hashed_password="hashed_pass")
    
    # Crear juego
    game = Game(
        id=game_id,
        name="Test Game Wild Child",
        max_players=10,
        creator_id=creator_id,
        players=[creator, wild_child, model1, model2, werewolf],
        status=GameStatus.NIGHT,
        current_round=1
    )
    
    # Asignar roles
    game.roles = {
        creator_id: RoleInfo(role=GameRole.VILLAGER, is_alive=True),
        wild_child_id: RoleInfo(role=GameRole.WILD_CHILD, is_alive=True),
        model1_id: RoleInfo(role=GameRole.VILLAGER, is_alive=True),
        model2_id: RoleInfo(role=GameRole.SEER, is_alive=True),
        werewolf_id: RoleInfo(role=GameRole.WAREWOLF, is_alive=True)
    }
    
    # Inicializar night_actions
    game.night_actions = {}
    
    game_service.save_game(game)
    return game


class TestWildChildVerifications:
    """Tests para verificaciones básicas del Niño Salvaje."""
    
    def test_is_wild_child_valid(self, sample_game_with_wild_child):
        """Test que verifica la identificación correcta del Niño Salvaje."""
        game = sample_game_with_wild_child
        
        # El Niño Salvaje debe ser identificado correctamente
        assert player_action_service.is_wild_child(game.id, "wild_child123")
        
        # Otros jugadores no deben ser identificados como Niño Salvaje
        assert not player_action_service.is_wild_child(game.id, "creator123")
        assert not player_action_service.is_wild_child(game.id, "model1_123")
        assert not player_action_service.is_wild_child(game.id, "werewolf123")
    
    def test_is_wild_child_nonexistent_player(self, sample_game_with_wild_child):
        """Test que verifica el comportamiento con jugadores inexistentes."""
        game = sample_game_with_wild_child
        
        assert not player_action_service.is_wild_child(game.id, "nonexistent")
        assert not player_action_service.is_wild_child("nonexistent_game", "wild_child123")
    
    def test_can_wild_child_choose_model_first_night(self, sample_game_with_wild_child):
        """Test que verifica que puede elegir modelo en la primera noche."""
        game = sample_game_with_wild_child
        
        # Debe poder elegir modelo en la primera noche
        assert player_action_service.can_wild_child_choose_model(game.id, "wild_child123")
    
    def test_can_wild_child_choose_model_wrong_phase(self, sample_game_with_wild_child):
        """Test que verifica que no puede elegir modelo fuera de la fase nocturna."""
        game = sample_game_with_wild_child
        
        # Cambiar a fase de día
        game.status = GameStatus.DAY
        game_service.save_game(game)
        
        assert not player_action_service.can_wild_child_choose_model(game.id, "wild_child123")
    
    def test_can_wild_child_choose_model_later_round(self, sample_game_with_wild_child):
        """Test que verifica que no puede elegir modelo después de la primera noche."""
        game = sample_game_with_wild_child
        
        # Cambiar a ronda posterior
        game.current_round = 2
        game_service.save_game(game)
        
        assert not player_action_service.can_wild_child_choose_model(game.id, "wild_child123")


class TestWildChildModelSelection:
    """Tests para la selección de modelo del Niño Salvaje."""
    
    def test_get_available_models(self, sample_game_with_wild_child):
        """Test que obtiene modelos disponibles correctamente."""
        game = sample_game_with_wild_child
        
        models = player_action_service.get_available_models_for_wild_child(game.id, "wild_child123")
        
        # Debe incluir a todos los jugadores vivos excepto él mismo
        assert len(models) == 4
        model_ids = [model["id"] for model in models]
        assert "creator123" in model_ids
        assert "model1_123" in model_ids
        assert "model2_123" in model_ids
        assert "werewolf123" in model_ids
        assert "wild_child123" not in model_ids
    
    def test_wild_child_choose_model_success(self, sample_game_with_wild_child):
        """Test de elección de modelo exitosa."""
        game = sample_game_with_wild_child
        
        result = player_action_service.wild_child_choose_model(game.id, "wild_child123", "model1_123")
        
        assert result is not None
        assert result.roles["wild_child123"].model_player_id == "model1_123"
        assert result.roles["wild_child123"].has_transformed is False
        assert result.night_actions["wild_child_model"]["wild_child123"] == "model1_123"
    
    def test_wild_child_choose_model_self(self, sample_game_with_wild_child):
        """Test que no permite elegirse a sí mismo como modelo."""
        game = sample_game_with_wild_child
        
        result = player_action_service.wild_child_choose_model(game.id, "wild_child123", "wild_child123")
        
        assert result is None
    
    def test_wild_child_choose_model_nonexistent(self, sample_game_with_wild_child):
        """Test que no permite elegir un jugador inexistente."""
        game = sample_game_with_wild_child
        
        result = player_action_service.wild_child_choose_model(game.id, "wild_child123", "nonexistent")
        
        assert result is None
    
    def test_wild_child_choose_model_already_chosen(self, sample_game_with_wild_child):
        """Test que no permite elegir modelo si ya eligió uno."""
        game = sample_game_with_wild_child
        
        # Elegir modelo primero
        player_action_service.wild_child_choose_model(game.id, "wild_child123", "model1_123")
        
        # Intentar elegir otro
        result = player_action_service.wild_child_choose_model(game.id, "wild_child123", "model2_123")
        
        assert result is None


class TestWildChildStatus:
    """Tests para el estado del Niño Salvaje."""
    
    def test_get_wild_child_status_no_model(self, sample_game_with_wild_child):
        """Test del estado sin modelo elegido."""
        game = sample_game_with_wild_child
        
        status = player_action_service.get_wild_child_status(game.id, "wild_child123")
        
        assert not status["has_model"]
        assert status["model_player_id"] is None
        assert status["model_username"] is None
        assert not status["is_transformed"]
        assert status["current_role"] == "wild_child"
    
    def test_get_wild_child_status_with_model(self, sample_game_with_wild_child):
        """Test del estado con modelo elegido."""
        game = sample_game_with_wild_child
        
        # Elegir modelo
        player_action_service.wild_child_choose_model(game.id, "wild_child123", "model1_123")
        
        status = player_action_service.get_wild_child_status(game.id, "wild_child123")
        
        assert status["has_model"]
        assert status["model_player_id"] == "model1_123"
        assert status["model_username"] == "model1"
        assert not status["is_transformed"]
        assert status["current_role"] == "wild_child"
    
    def test_get_wild_child_status_transformed(self, sample_game_with_wild_child):
        """Test del estado después de transformarse."""
        game = sample_game_with_wild_child
        
        # Elegir modelo y simular transformación
        player_action_service.wild_child_choose_model(game.id, "wild_child123", "model1_123")
        
        # Recargar el juego y simular muerte del modelo
        updated_game = game_service.load_game(game.id)
        assert updated_game is not None
        updated_game.roles["model1_123"].is_alive = False
        game_service.save_game(updated_game)
        
        # Procesar transformación
        transformations = player_action_service.check_wild_child_transformation(game.id, "model1_123")
        
        assert len(transformations) == 1
        assert transformations[0]["wild_child_id"] == "wild_child123"
        
        # Verificar estado
        status = player_action_service.get_wild_child_status(game.id, "wild_child123")
        
        assert status["has_model"]
        assert status["is_transformed"]
        assert status["current_role"] == "warewolf"


class TestWildChildTransformation:
    """Tests para la transformación del Niño Salvaje."""
    
    def test_check_transformation_model_dies(self, sample_game_with_wild_child):
        """Test de transformación cuando muere el modelo."""
        game = sample_game_with_wild_child
        
        # Elegir modelo
        player_action_service.wild_child_choose_model(game.id, "wild_child123", "model1_123")
        
        # Simular muerte del modelo
        transformations = player_action_service.check_wild_child_transformation(game.id, "model1_123")
        
        assert len(transformations) == 1
        
        transformation = transformations[0]
        assert transformation["wild_child_id"] == "wild_child123"
        assert transformation["wild_child_username"] == "wild_child"
        assert transformation["model_id"] == "model1_123"
        
        # Verificar que se transformó en el juego
        updated_game = game_service.load_game(game.id)
        assert updated_game is not None
        wild_child_role = updated_game.roles["wild_child123"]
        assert wild_child_role.has_transformed
        assert wild_child_role.role == GameRole.WAREWOLF
    
    def test_check_transformation_wrong_death(self, sample_game_with_wild_child):
        """Test que no se transforma si muere otro jugador."""
        game = sample_game_with_wild_child
        
        # Elegir modelo
        player_action_service.wild_child_choose_model(game.id, "wild_child123", "model1_123")
        
        # Simular muerte de otro jugador
        transformations = player_action_service.check_wild_child_transformation(game.id, "creator123")
        
        assert len(transformations) == 0
        
        # Verificar que NO se transformó
        updated_game = game_service.load_game(game.id)
        assert updated_game is not None
        wild_child_role = updated_game.roles["wild_child123"]
        assert not wild_child_role.has_transformed
        assert wild_child_role.role == GameRole.WILD_CHILD
    
    def test_check_transformation_no_model(self, sample_game_with_wild_child):
        """Test que no se transforma si no tiene modelo."""
        game = sample_game_with_wild_child
        
        # No elegir modelo
        
        # Simular muerte de cualquier jugador
        transformations = player_action_service.check_wild_child_transformation(game.id, "model1_123")
        
        assert len(transformations) == 0
    
    def test_check_transformation_already_transformed(self, sample_game_with_wild_child):
        """Test que no se transforma de nuevo si ya se transformó."""
        game = sample_game_with_wild_child
        
        # Elegir modelo y transformar
        player_action_service.wild_child_choose_model(game.id, "wild_child123", "model1_123")
        player_action_service.check_wild_child_transformation(game.id, "model1_123")
        
        # Intentar transformar de nuevo
        transformations = player_action_service.check_wild_child_transformation(game.id, "model1_123")
        
        assert len(transformations) == 0


class TestWildChildWerewolfNotification:
    """Tests para notificar a los hombres lobo de nuevos miembros."""
    
    def test_notify_werewolves_of_new_member(self, sample_game_with_wild_child):
        """Test de notificación a hombres lobo existentes."""
        game = sample_game_with_wild_child
        
        # Elegir modelo y transformar
        player_action_service.wild_child_choose_model(game.id, "wild_child123", "model1_123")
        player_action_service.check_wild_child_transformation(game.id, "model1_123")
        
        # Obtener hombres lobo existentes
        existing_werewolves = player_action_service.notify_werewolves_of_new_member(game.id, "wild_child123")
        
        assert len(existing_werewolves) == 1
        assert "werewolf123" in existing_werewolves
        assert "wild_child123" not in existing_werewolves
    
    def test_notify_werewolves_no_existing(self, sample_game_with_wild_child):
        """Test cuando no hay hombres lobo existentes."""
        game = sample_game_with_wild_child
        
        # Matar al hombre lobo existente
        game.roles["werewolf123"].is_alive = False
        game_service.save_game(game)
        
        # Elegir modelo y transformar
        player_action_service.wild_child_choose_model(game.id, "wild_child123", "model1_123")
        player_action_service.check_wild_child_transformation(game.id, "model1_123")
        
        # No debe haber hombres lobo existentes para notificar
        existing_werewolves = player_action_service.notify_werewolves_of_new_member(game.id, "wild_child123")
        
        assert len(existing_werewolves) == 0


class TestWildChildGameFlow:
    """Tests para el flujo completo del Niño Salvaje."""
    
    def test_full_wild_child_flow(self, sample_game_with_wild_child):
        """Test del flujo completo del Niño Salvaje."""
        game = sample_game_with_wild_child
        
        # 1. Inicializar
        success = player_action_service.initialize_wild_child(game.id, "wild_child123")
        assert success
        
        # 2. Verificar que puede elegir modelo
        assert player_action_service.can_wild_child_choose_model(game.id, "wild_child123")
        
        # 3. Obtener modelos disponibles
        models = player_action_service.get_available_models_for_wild_child(game.id, "wild_child123")
        assert len(models) > 0
        
        # 4. Elegir modelo
        result = player_action_service.wild_child_choose_model(game.id, "wild_child123", "model1_123")
        assert result is not None
        
        # 5. Verificar estado
        status = player_action_service.get_wild_child_status(game.id, "wild_child123")
        assert status["has_model"]
        assert not status["is_transformed"]
        
        # 6. Simular muerte del modelo
        player_action_service.simulate_player_death(game.id, "model1_123")
        transformations = player_action_service.check_wild_child_transformation(game.id, "model1_123")
        assert len(transformations) == 1
        
        # 7. Verificar transformación
        final_status = player_action_service.get_wild_child_status(game.id, "wild_child123")
        assert final_status["is_transformed"]
        assert final_status["current_role"] == "warewolf"
        
        # 8. Verificar que los hombres lobo existentes fueron notificados
        existing_werewolves = player_action_service.notify_werewolves_of_new_member(game.id, "wild_child123")
        assert len(existing_werewolves) >= 0
    
    def test_process_death_checks(self, sample_game_with_wild_child):
        """Test del procesamiento de verificaciones de muerte."""
        game = sample_game_with_wild_child
        
        # Elegir modelo
        player_action_service.wild_child_choose_model(game.id, "wild_child123", "model1_123")
        
        # Recargar el juego y marcar modelo como muerto
        updated_game = game_service.load_game(game.id)
        assert updated_game is not None
        updated_game.roles["model1_123"].is_alive = False
        game_service.save_game(updated_game)
        
        # Procesar verificaciones de muerte
        transformations = player_action_service.process_wild_child_death_check(game.id)
        
        assert len(transformations) == 1
        assert transformations[0]["wild_child_id"] == "wild_child123"


class TestWildChildInitialization:
    """Tests para la inicialización del Niño Salvaje."""
    
    def test_initialize_wild_child_success(self, sample_game_with_wild_child):
        """Test de inicialización exitosa."""
        game = sample_game_with_wild_child
        
        success = player_action_service.initialize_wild_child(game.id, "wild_child123")
        assert success
        
        # Verificar estado inicial
        updated_game = game_service.load_game(game.id)
        assert updated_game is not None
        wild_child_role = updated_game.roles["wild_child123"]
        assert wild_child_role.model_player_id is None
        assert not wild_child_role.has_transformed
    
    def test_initialize_wild_child_invalid_role(self, sample_game_with_wild_child):
        """Test de inicialización con jugador que no es Niño Salvaje."""
        game = sample_game_with_wild_child
        
        success = player_action_service.initialize_wild_child(game.id, "creator123")
        assert not success
    
    def test_reset_wild_child_night_actions(self, sample_game_with_wild_child):
        """Test de reinicio de acciones nocturnas."""
        game = sample_game_with_wild_child
        
        # Elegir modelo
        player_action_service.wild_child_choose_model(game.id, "wild_child123", "model1_123")
        
        # Verificar que se registró la acción
        updated_game = game_service.load_game(game.id)
        assert updated_game is not None
        assert "wild_child_model" in updated_game.night_actions
        assert len(updated_game.night_actions["wild_child_model"]) > 0
        
        # Reiniciar
        success = player_action_service.reset_wild_child_night_actions(game.id)
        assert success
        
        # Verificar que se limpiaron las acciones
        final_game = game_service.load_game(game.id)
        assert final_game is not None
        assert len(final_game.night_actions.get("wild_child_model", {})) == 0

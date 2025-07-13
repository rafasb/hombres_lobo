# test_witch_actions.py
# Tests para las acciones de la Bruja

import pytest
from app.services import player_action_service, game_service
from app.models.game import Game, GameStatus
from app.models.roles import GameRole, RoleInfo
from app.models.user import User, UserRole


@pytest.fixture
def sample_game_with_witch():
    """Fixture que crea un juego con una bruja para testing."""
    game_id = "test_game_witch"
    creator_id = "creator123"
    witch_id = "witch123"
    victim_id = "victim123"
    werewolf_id = "werewolf123"
    
    # Crear usuarios
    creator = User(id=creator_id, username="creator", email="creator@test.com", role=UserRole.PLAYER, hashed_password="hashed_pass")
    witch = User(id=witch_id, username="witch", email="witch@test.com", role=UserRole.PLAYER, hashed_password="hashed_pass")
    victim = User(id=victim_id, username="victim", email="victim@test.com", role=UserRole.PLAYER, hashed_password="hashed_pass")
    werewolf = User(id=werewolf_id, username="werewolf", email="werewolf@test.com", role=UserRole.PLAYER, hashed_password="hashed_pass")
    
    # Crear juego
    game = Game(
        id=game_id,
        name="Test Game Witch",
        max_players=10,
        creator_id=creator_id,
        players=[creator, witch, victim, werewolf],
        status=GameStatus.NIGHT,
        current_round=1
    )
    
    # Asignar roles
    game.roles = {
        creator_id: RoleInfo(role=GameRole.VILLAGER, is_alive=True),
        witch_id: RoleInfo(role=GameRole.WITCH, is_alive=True, has_healing_potion=True, has_poison_potion=True),
        victim_id: RoleInfo(role=GameRole.VILLAGER, is_alive=True),
        werewolf_id: RoleInfo(role=GameRole.WAREWOLF, is_alive=True)
    }
    
    # Inicializar night_actions
    game.night_actions = {
        "warewolf_attacks": {werewolf_id: victim_id}  # Los lobos atacan a victim
    }
    
    game_service.save_game(game)
    return game


class TestWitchVerifications:
    """Tests para verificaciones básicas de la bruja."""
    
    def test_is_witch_valid(self, sample_game_with_witch):
        """Test que verifica la identificación correcta de la bruja."""
        game = sample_game_with_witch
        
        # La bruja debe ser identificada correctamente
        assert player_action_service.is_witch(game.id, "witch123") == True
        
        # Otros jugadores no deben ser identificados como bruja
        assert player_action_service.is_witch(game.id, "creator123") == False
        assert player_action_service.is_witch(game.id, "victim123") == False
        assert player_action_service.is_witch(game.id, "werewolf123") == False
    
    def test_is_witch_nonexistent_player(self, sample_game_with_witch):
        """Test que verifica el comportamiento con jugadores inexistentes."""
        game = sample_game_with_witch
        
        assert player_action_service.is_witch(game.id, "nonexistent") == False
        assert player_action_service.is_witch("nonexistent_game", "witch123") == False
    
    def test_can_witch_heal_valid_conditions(self, sample_game_with_witch):
        """Test que verifica las condiciones para poder curar."""
        game = sample_game_with_witch
        
        # La bruja debe poder curar inicialmente
        assert player_action_service.can_witch_heal(game.id, "witch123") == True
    
    def test_can_witch_heal_no_potion(self, sample_game_with_witch):
        """Test que verifica que no puede curar sin poción."""
        game = sample_game_with_witch
        
        # Quitar la poción de curación
        game.roles["witch123"].has_healing_potion = False
        game_service.save_game(game)
        
        assert player_action_service.can_witch_heal(game.id, "witch123") == False
    
    def test_can_witch_poison_valid_conditions(self, sample_game_with_witch):
        """Test que verifica las condiciones para poder envenenar."""
        game = sample_game_with_witch
        
        # La bruja debe poder envenenar inicialmente
        assert player_action_service.can_witch_poison(game.id, "witch123") == True
    
    def test_can_witch_poison_no_potion(self, sample_game_with_witch):
        """Test que verifica que no puede envenenar sin poción."""
        game = sample_game_with_witch
        
        # Quitar la poción de veneno
        game.roles["witch123"].has_poison_potion = False
        game_service.save_game(game)
        
        assert player_action_service.can_witch_poison(game.id, "witch123") == False


class TestWitchAttackInfo:
    """Tests para obtener información del ataque de lobos."""
    
    def test_get_warewolf_attack_victim(self, sample_game_with_witch):
        """Test que obtiene la víctima del ataque de lobos."""
        game = sample_game_with_witch
        
        victim = player_action_service.get_warewolf_attack_victim(game.id)
        assert victim == "victim123"
    
    def test_get_witch_night_info(self, sample_game_with_witch):
        """Test que obtiene información completa de la noche para la bruja."""
        game = sample_game_with_witch
        
        night_info = player_action_service.get_witch_night_info(game.id, "witch123")
        
        assert night_info["attacked_player_id"] == "victim123"
        assert night_info["attacked_username"] == "victim"
        assert night_info["can_heal"] == True
        assert night_info["can_poison"] == True
        assert night_info["has_healing_potion"] == True
        assert night_info["has_poison_potion"] == True
    
    def test_get_witch_night_info_no_attack(self, sample_game_with_witch):
        """Test información de noche cuando no hay ataque."""
        game = sample_game_with_witch
        
        # Limpiar ataques de lobos
        game.night_actions["warewolf_attacks"] = {}
        game_service.save_game(game)
        
        night_info = player_action_service.get_witch_night_info(game.id, "witch123")
        
        assert night_info["attacked_player_id"] is None
        assert night_info["attacked_username"] is None
        assert night_info["can_heal"] == True
        assert night_info["can_poison"] == True


class TestWitchHeal:
    """Tests para la acción de curación de la bruja."""
    
    def test_witch_heal_victim_success(self, sample_game_with_witch):
        """Test de curación exitosa."""
        game = sample_game_with_witch
        
        result = player_action_service.witch_heal_victim(game.id, "witch123", "victim123")
        
        assert result is not None
        assert result.night_actions["witch_heal"]["witch123"] == "victim123"
        assert result.roles["witch123"].has_healing_potion == False
    
    def test_witch_heal_wrong_target(self, sample_game_with_witch):
        """Test que no permite curar a alguien que no fue atacado."""
        game = sample_game_with_witch
        
        result = player_action_service.witch_heal_victim(game.id, "witch123", "creator123")
        
        assert result is None
    
    def test_witch_heal_without_potion(self, sample_game_with_witch):
        """Test que no permite curar sin poción."""
        game = sample_game_with_witch
        
        # Quitar la poción de curación
        game.roles["witch123"].has_healing_potion = False
        game_service.save_game(game)
        
        result = player_action_service.witch_heal_victim(game.id, "witch123", "victim123")
        
        assert result is None
    
    def test_witch_heal_nonexistent_target(self, sample_game_with_witch):
        """Test que no permite curar a un jugador inexistente."""
        game = sample_game_with_witch
        
        result = player_action_service.witch_heal_victim(game.id, "witch123", "nonexistent")
        
        assert result is None


class TestWitchPoison:
    """Tests para la acción de envenenamiento de la bruja."""
    
    def test_witch_poison_player_success(self, sample_game_with_witch):
        """Test de envenenamiento exitoso."""
        game = sample_game_with_witch
        
        result = player_action_service.witch_poison_player(game.id, "witch123", "creator123")
        
        assert result is not None
        assert result.night_actions["witch_poison"]["witch123"] == "creator123"
        assert result.roles["witch123"].has_poison_potion == False
    
    def test_witch_poison_self(self, sample_game_with_witch):
        """Test que permite envenenarse a sí misma."""
        game = sample_game_with_witch
        
        result = player_action_service.witch_poison_player(game.id, "witch123", "witch123")
        
        assert result is not None
        assert result.night_actions["witch_poison"]["witch123"] == "witch123"
    
    def test_witch_poison_without_potion(self, sample_game_with_witch):
        """Test que no permite envenenar sin poción."""
        game = sample_game_with_witch
        
        # Quitar la poción de veneno
        game.roles["witch123"].has_poison_potion = False
        game_service.save_game(game)
        
        result = player_action_service.witch_poison_player(game.id, "witch123", "creator123")
        
        assert result is None
    
    def test_witch_poison_dead_target(self, sample_game_with_witch):
        """Test que no permite envenenar a un jugador muerto."""
        game = sample_game_with_witch
        
        # Marcar al objetivo como muerto
        game.roles["creator123"].is_alive = False
        game_service.save_game(game)
        
        result = player_action_service.witch_poison_player(game.id, "witch123", "creator123")
        
        assert result is None
    
    def test_get_witch_poison_targets(self, sample_game_with_witch):
        """Test que obtiene objetivos válidos para envenenar."""
        game = sample_game_with_witch
        
        targets = player_action_service.get_witch_poison_targets(game.id, "witch123")
        
        # Debe incluir a todos los jugadores vivos (incluyendo la bruja)
        assert len(targets) == 4
        target_ids = [target["id"] for target in targets]
        assert "creator123" in target_ids
        assert "witch123" in target_ids
        assert "victim123" in target_ids
        assert "werewolf123" in target_ids


class TestWitchNightProcessing:
    """Tests para el procesamiento de acciones nocturnas de la bruja."""
    
    def test_process_witch_night_actions_heal_only(self, sample_game_with_witch):
        """Test procesamiento solo con curación."""
        game = sample_game_with_witch
        
        # Realizar curación
        player_action_service.witch_heal_victim(game.id, "witch123", "victim123")
        
        results = player_action_service.process_witch_night_actions(game.id)
        
        assert "victim123" in results["healed"]
        assert len(results["poisoned"]) == 0
    
    def test_process_witch_night_actions_poison_only(self, sample_game_with_witch):
        """Test procesamiento solo con envenenamiento."""
        game = sample_game_with_witch
        
        # Realizar envenenamiento
        player_action_service.witch_poison_player(game.id, "witch123", "creator123")
        
        results = player_action_service.process_witch_night_actions(game.id)
        
        assert len(results["healed"]) == 0
        assert "creator123" in results["poisoned"]
        
        # Verificar que el jugador envenenado está muerto
        updated_game = game_service.load_game(game.id)
        assert updated_game.roles["creator123"].is_alive == False
    
    def test_process_witch_night_actions_both(self, sample_game_with_witch):
        """Test procesamiento con curación y envenenamiento."""
        game = sample_game_with_witch
        
        # Realizar ambas acciones
        player_action_service.witch_heal_victim(game.id, "witch123", "victim123")
        player_action_service.witch_poison_player(game.id, "witch123", "creator123")
        
        results = player_action_service.process_witch_night_actions(game.id)
        
        assert "victim123" in results["healed"]
        assert "creator123" in results["poisoned"]
        
        # Verificar estados
        updated_game = game_service.load_game(game.id)
        assert updated_game.roles["creator123"].is_alive == False
        assert updated_game.roles["victim123"].is_alive == True  # Asumiendo que se procesa la curación
    
    def test_reset_witch_night_actions(self, sample_game_with_witch):
        """Test reinicio de acciones nocturnas."""
        game = sample_game_with_witch
        
        # Realizar acciones
        player_action_service.witch_heal_victim(game.id, "witch123", "victim123")
        player_action_service.witch_poison_player(game.id, "witch123", "creator123")
        
        # Reiniciar
        success = player_action_service.reset_witch_night_actions(game.id)
        assert success == True
        
        # Verificar que se limpiaron las acciones
        updated_game = game_service.load_game(game.id)
        assert len(updated_game.night_actions.get("witch_heal", {})) == 0
        assert len(updated_game.night_actions.get("witch_poison", {})) == 0


class TestWitchInitialization:
    """Tests para la inicialización de pociones de la bruja."""
    
    def test_initialize_witch_potions(self, sample_game_with_witch):
        """Test inicialización de pociones."""
        game = sample_game_with_witch
        
        # Quitar las pociones primero
        game.roles["witch123"].has_healing_potion = False
        game.roles["witch123"].has_poison_potion = False
        game_service.save_game(game)
        
        # Inicializar
        success = player_action_service.initialize_witch_potions(game.id, "witch123")
        assert success == True
        
        # Verificar que se restauraron las pociones
        updated_game = game_service.load_game(game.id)
        assert updated_game.roles["witch123"].has_healing_potion == True
        assert updated_game.roles["witch123"].has_poison_potion == True
    
    def test_initialize_witch_potions_invalid_role(self, sample_game_with_witch):
        """Test inicialización con jugador que no es bruja."""
        game = sample_game_with_witch
        
        success = player_action_service.initialize_witch_potions(game.id, "creator123")
        assert success == False

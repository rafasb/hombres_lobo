"""
Tests para las acciones de Cupido.
"""

import pytest
from app.models.game_and_roles import Game, RoleInfo, GameRole, GameStatus
from app.models.user import User, UserRole
from app.services import player_action_service, game_service


@pytest.fixture
def sample_game_with_cupid():
    """Fixture que crea un juego con Cupido para testing."""
    game_id = "test_game_cupid"
    creator_id = "creator123"
    cupid_id = "cupid123"
    target1_id = "target1_123"
    target2_id = "target2_123"
    werewolf_id = "werewolf123"
    
    # Crear usuarios
    creator = User(id=creator_id, username="creator", email="creator@test.com", role=UserRole.PLAYER, hashed_password="hashed_pass")
    cupid = User(id=cupid_id, username="cupido", email="cupid@test.com", role=UserRole.PLAYER, hashed_password="hashed_pass")
    target1 = User(id=target1_id, username="target1", email="target1@test.com", role=UserRole.PLAYER, hashed_password="hashed_pass")
    target2 = User(id=target2_id, username="target2", email="target2@test.com", role=UserRole.PLAYER, hashed_password="hashed_pass")
    werewolf = User(id=werewolf_id, username="werewolf", email="werewolf@test.com", role=UserRole.PLAYER, hashed_password="hashed_pass")
    
    # Crear juego
    game = Game(
        id=game_id,
        name="Test Game Cupid",
        max_players=10,
        creator_id=creator_id,
        players=[creator, cupid, target1, target2, werewolf],
        status=GameStatus.NIGHT,
        current_round=1
    )
    
    # Asignar roles
    game.roles = {
        creator_id: RoleInfo(role=GameRole.VILLAGER, is_alive=True),
        cupid_id: RoleInfo(role=GameRole.CUPID, is_alive=True),
        target1_id: RoleInfo(role=GameRole.VILLAGER, is_alive=True),
        target2_id: RoleInfo(role=GameRole.SEER, is_alive=True),
        werewolf_id: RoleInfo(role=GameRole.WAREWOLF, is_alive=True)
    }
    
    # Inicializar night_actions
    game.night_actions = {}
    
    game_service.save_game(game)
    return game


class TestCupidVerifications:
    """Tests para verificaciones básicas de Cupido."""
    
    def test_is_cupid_valid(self, sample_game_with_cupid):
        """Test que verifica la identificación correcta de Cupido."""
        game = sample_game_with_cupid
        
        # Cupido debe ser identificado correctamente
        assert player_action_service.is_cupid(game.id, "cupid123")
        
        # Otros jugadores no deben ser identificados como Cupido
        assert not player_action_service.is_cupid(game.id, "creator123")
        assert not player_action_service.is_cupid(game.id, "target1_123")
        assert not player_action_service.is_cupid(game.id, "werewolf123")
    
    def test_is_cupid_nonexistent_player(self, sample_game_with_cupid):
        """Test que verifica el comportamiento con jugadores inexistentes."""
        game = sample_game_with_cupid
        
        assert not player_action_service.is_cupid(game.id, "nonexistent")
        assert not player_action_service.is_cupid("nonexistent_game", "cupid123")
    
    def test_can_cupid_choose_lovers_first_night(self, sample_game_with_cupid):
        """Test que verifica que puede elegir enamorados en la primera noche."""
        game = sample_game_with_cupid
        
        assert player_action_service.can_cupid_choose_lovers(game.id, "cupid123")
    
    def test_can_cupid_choose_lovers_wrong_phase(self, sample_game_with_cupid):
        """Test que verifica que no puede elegir enamorados en fase de día."""
        game = sample_game_with_cupid
        
        # Cambiar a fase de día
        game.status = GameStatus.DAY
        game_service.save_game(game)
        
        assert not player_action_service.can_cupid_choose_lovers(game.id, "cupid123")
    
    def test_can_cupid_choose_lovers_later_round(self, sample_game_with_cupid):
        """Test que verifica que no puede elegir enamorados después de la primera noche."""
        game = sample_game_with_cupid
        
        # Cambiar a ronda 2
        game.current_round = 2
        game_service.save_game(game)
        
        assert not player_action_service.can_cupid_choose_lovers(game.id, "cupid123")


class TestCupidTargetSelection:
    """Tests para la selección de objetivos de Cupido."""
    
    def test_get_available_targets(self, sample_game_with_cupid):
        """Test que obtiene objetivos disponibles para enamorar."""
        game = sample_game_with_cupid
        
        targets = player_action_service.get_cupid_available_targets(game.id, "cupid123")
        
        # Debe incluir a todos los jugadores vivos (incluyendo a Cupido)
        assert len(targets) == 5
        target_ids = [target["id"] for target in targets]
        assert "creator123" in target_ids
        assert "cupid123" in target_ids
        assert "target1_123" in target_ids
        assert "target2_123" in target_ids
        assert "werewolf123" in target_ids
    
    def test_cupid_choose_lovers_success(self, sample_game_with_cupid):
        """Test de elección exitosa de enamorados."""
        game = sample_game_with_cupid
        
        result = player_action_service.cupid_choose_lovers(game.id, "cupid123", "target1_123", "target2_123")
        
        assert result is not None
        
        # Verificar que los jugadores están marcados como enamorados
        updated_game = game_service.load_game(game.id)
        assert updated_game is not None
        assert updated_game.roles["target1_123"].is_lover
        assert updated_game.roles["target2_123"].is_lover
        assert updated_game.roles["target1_123"].lover_partner_id == "target2_123"
        assert updated_game.roles["target2_123"].lover_partner_id == "target1_123"
    
    def test_cupid_choose_lovers_same_target(self, sample_game_with_cupid):
        """Test que impide elegir al mismo jugador como ambos enamorados."""
        game = sample_game_with_cupid
        
        result = player_action_service.cupid_choose_lovers(game.id, "cupid123", "target1_123", "target1_123")
        
        assert result is None
    
    def test_cupid_choose_lovers_nonexistent_target(self, sample_game_with_cupid):
        """Test que impide elegir jugadores inexistentes."""
        game = sample_game_with_cupid
        
        result = player_action_service.cupid_choose_lovers(game.id, "cupid123", "nonexistent", "target1_123")
        
        assert result is None
    
    def test_cupid_choose_lovers_already_chosen(self, sample_game_with_cupid):
        """Test que impide elegir enamorados si ya se eligieron."""
        game = sample_game_with_cupid
        
        # Primera elección exitosa
        player_action_service.cupid_choose_lovers(game.id, "cupid123", "target1_123", "target2_123")
        
        # Segunda elección debe fallar
        result = player_action_service.cupid_choose_lovers(game.id, "cupid123", "creator123", "werewolf123")
        
        assert result is None


class TestCupidStatus:
    """Tests para el estado de Cupido."""
    
    def test_get_cupid_status_no_lovers(self, sample_game_with_cupid):
        """Test del estado antes de elegir enamorados."""
        game = sample_game_with_cupid
        
        status = player_action_service.get_cupid_status(game.id, "cupid123")
        
        assert not status["has_chosen_lovers"]
        assert status["lover1_id"] is None
        assert status["lover2_id"] is None
    
    def test_get_cupid_status_with_lovers(self, sample_game_with_cupid):
        """Test del estado después de elegir enamorados."""
        game = sample_game_with_cupid
        
        # Elegir enamorados
        player_action_service.cupid_choose_lovers(game.id, "cupid123", "target1_123", "target2_123")
        
        # Verificar estado
        status = player_action_service.get_cupid_status(game.id, "cupid123")
        
        assert status["has_chosen_lovers"]
        assert status["lover1_id"] == "target1_123"
        assert status["lover2_id"] == "target2_123"
        assert status["lover1_username"] == "target1"
        assert status["lover2_username"] == "target2"


class TestLoversStatus:
    """Tests para el estado de los enamorados."""
    
    def test_get_lovers_status_not_lover(self, sample_game_with_cupid):
        """Test del estado de un jugador que no es enamorado."""
        game = sample_game_with_cupid
        
        status = player_action_service.get_lovers_status(game.id, "creator123")
        
        assert not status["is_lover"]
        assert status["partner_id"] is None
        assert status["partner_username"] is None
        assert not status["both_alive"]
    
    def test_get_lovers_status_is_lover(self, sample_game_with_cupid):
        """Test del estado de un jugador que es enamorado."""
        game = sample_game_with_cupid
        
        # Elegir enamorados
        player_action_service.cupid_choose_lovers(game.id, "cupid123", "target1_123", "target2_123")
        
        # Verificar estado del primer enamorado
        status1 = player_action_service.get_lovers_status(game.id, "target1_123")
        
        assert status1["is_lover"]
        assert status1["partner_id"] == "target2_123"
        assert status1["partner_username"] == "target2"
        assert status1["both_alive"]
        
        # Verificar estado del segundo enamorado
        status2 = player_action_service.get_lovers_status(game.id, "target2_123")
        
        assert status2["is_lover"]
        assert status2["partner_id"] == "target1_123"
        assert status2["partner_username"] == "target1"
        assert status2["both_alive"]


class TestLoversDeathMechanic:
    """Tests para la mecánica de muerte de enamorados."""
    
    def test_check_lovers_death_partner_dies(self, sample_game_with_cupid):
        """Test que verifica que un enamorado muere cuando muere su pareja."""
        game = sample_game_with_cupid
        
        # Elegir enamorados
        player_action_service.cupid_choose_lovers(game.id, "cupid123", "target1_123", "target2_123")
        
        # Matar al primer enamorado
        game = game_service.load_game(game.id)
        assert game is not None
        game.roles["target1_123"].is_alive = False
        game_service.save_game(game)
        
        # Verificar muerte por amor
        deaths = player_action_service.check_lovers_death(game.id, "target1_123")
        
        assert len(deaths) == 1
        assert "target2_123" in deaths
        
        # Verificar que el segundo enamorado está muerto
        updated_game = game_service.load_game(game.id)
        assert updated_game is not None
        assert not updated_game.roles["target2_123"].is_alive
    
    def test_check_lovers_death_no_partner(self, sample_game_with_cupid):
        """Test que verifica que no pasa nada si muere un no-enamorado."""
        game = sample_game_with_cupid
        
        # Matar a un jugador que no es enamorado
        game.roles["creator123"].is_alive = False
        game_service.save_game(game)
        
        # Verificar que no hay muertes por amor
        deaths = player_action_service.check_lovers_death(game.id, "creator123")
        
        assert len(deaths) == 0


class TestLoversVictory:
    """Tests para la condición de victoria de los enamorados."""
    
    def test_check_lovers_victory_condition_win(self, sample_game_with_cupid):
        """Test que verifica la victoria de los enamorados."""
        game = sample_game_with_cupid
        
        # Elegir enamorados
        player_action_service.cupid_choose_lovers(game.id, "cupid123", "target1_123", "werewolf123")
        
        # Matar a todos excepto los enamorados
        game = game_service.load_game(game.id)
        assert game is not None
        game.roles["creator123"].is_alive = False
        game.roles["cupid123"].is_alive = False
        game.roles["target2_123"].is_alive = False
        game_service.save_game(game)
        
        # Verificar condición de victoria
        victory_info = player_action_service.check_lovers_victory_condition(game.id)
        
        assert victory_info is not None
        assert victory_info["victory_type"] == "lovers"
        assert len(victory_info["winners"]) == 2
        
        winner_ids = [winner["id"] for winner in victory_info["winners"]]
        assert "target1_123" in winner_ids
        assert "werewolf123" in winner_ids
    
    def test_check_lovers_victory_condition_no_win(self, sample_game_with_cupid):
        """Test que verifica que no hay victoria si hay más de 2 jugadores vivos."""
        game = sample_game_with_cupid
        
        # Elegir enamorados
        player_action_service.cupid_choose_lovers(game.id, "cupid123", "target1_123", "target2_123")
        
        # Verificar que no hay victoria (todos están vivos)
        victory_info = player_action_service.check_lovers_victory_condition(game.id)
        
        assert victory_info is None


class TestCupidInitialization:
    """Tests para la inicialización de Cupido."""
    
    def test_initialize_cupid_success(self, sample_game_with_cupid):
        """Test de inicialización exitosa."""
        game = sample_game_with_cupid
        
        success = player_action_service.initialize_cupid_night_actions(game.id, "cupid123")
        assert success
        
        # Verificar que se marcó como Cupido
        updated_game = game_service.load_game(game.id)
        assert updated_game is not None
        assert updated_game.roles["cupid123"].is_cupid
    
    def test_initialize_cupid_invalid_role(self, sample_game_with_cupid):
        """Test de inicialización con jugador que no es Cupido."""
        game = sample_game_with_cupid
        
        success = player_action_service.initialize_cupid_night_actions(game.id, "creator123")
        assert not success
    
    def test_reset_cupid_night_actions(self, sample_game_with_cupid):
        """Test de reinicio de acciones nocturnas."""
        game = sample_game_with_cupid
        
        # Realizar acción
        player_action_service.cupid_choose_lovers(game.id, "cupid123", "target1_123", "target2_123")
        
        # Reiniciar
        success = player_action_service.reset_cupid_night_actions(game.id)
        assert success
        
        # Verificar que se limpiaron las acciones
        updated_game = game_service.load_game(game.id)
        assert updated_game is not None
        assert len(updated_game.night_actions.get("cupid_lovers", {})) == 0

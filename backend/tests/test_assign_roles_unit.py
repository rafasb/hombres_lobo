"""
Test unitario para la función assign_roles
Valida la correcta asignación de roles según las reglas del juego
"""

from unittest.mock import patch
from app.services.game_flow_service import assign_roles
from app.models.game_and_roles import Game, GameStatus, GameRole
from app.models.user import User, UserRole, UserStatus
import uuid
import datetime


class TestAssignRoles:
    """Clase de tests para la función assign_roles"""

    def create_mock_user(self, user_id=None, username=None):
        """Crea un usuario mock para testing"""
        if user_id is None:
            user_id = str(uuid.uuid4())
        if username is None:
            username = f"player_{user_id[:8]}"
        
        return User(
            id=user_id,
            username=username,
            email=f"{username}@test.com",
            role=UserRole.PLAYER,
            status=UserStatus.ACTIVE,
            hashed_password="mock_hash",
            created_at=datetime.datetime.now(datetime.UTC),
            updated_at=datetime.datetime.now(datetime.UTC)
        )

    def create_mock_game(self, num_players=10, creator_id=None):
        """Crea una partida mock con el número especificado de jugadores"""
        if creator_id is None:
            creator_id = str(uuid.uuid4())
        
        # Crear jugadores incluyendo el creador
        player_ids = []
        creator = self.create_mock_user(creator_id, "creator")
        player_ids.append(creator.id)
        
        # Agregar jugadores adicionales
        for i in range(num_players - 1):
            player = self.create_mock_user(username=f"player_{i}")
            player_ids.append(player.id)
        
        return Game(
            id=str(uuid.uuid4()),
            name="Test Game",
            creator_id=creator_id,
            players=player_ids,  # Ahora solo almacenamos IDs
            roles={},
            status=GameStatus.WAITING,
            max_players=18,
            created_at=datetime.datetime.now(datetime.UTC),
            current_round=0
        )

    @patch('app.services.game_flow_service.load_game')
    @patch('app.services.game_flow_service.save_game')
    def test_assign_roles_valid_game_10_players(self, mock_save, mock_load):
        """Test con 10 jugadores (mínimo requerido)"""
        # Arrange
        creator_id = str(uuid.uuid4())
        game = self.create_mock_game(10, creator_id)
        mock_load.return_value = game

        # Act
        result = assign_roles(game.id, creator_id, is_admin=False)

        # Assert
        assert result is not None
        assert result.status == GameStatus.STARTED
        assert result.current_round == 1
        assert len(result.roles) == 10
        
        # Verificar número de hombres lobo (10 // 3 = 3)
        warewolf_count = sum(1 for role_info in result.roles.values() 
                           if role_info.role == GameRole.WAREWOLF)
        assert warewolf_count == 3
        
        # Verificar que hay roles especiales
        roles_list = [role_info.role for role_info in result.roles.values()]
        assert GameRole.SEER in roles_list
        assert GameRole.WITCH in roles_list
        assert GameRole.HUNTER in roles_list
        assert GameRole.CUPID in roles_list
        
        # El resto deben ser aldeanos (10 - 3 lobos - 4 especiales = 3 aldeanos)
        villager_count = sum(1 for role_info in result.roles.values() 
                           if role_info.role == GameRole.VILLAGER)
        assert villager_count == 3
        
        # Verificar habilidades específicas
        witch_role = next((role_info for role_info in result.roles.values() 
                          if role_info.role == GameRole.WITCH), None)
        assert witch_role is not None
        assert witch_role.has_healing_potion is True
        assert witch_role.has_poison_potion is True
        
        cupid_role = next((role_info for role_info in result.roles.values() 
                          if role_info.role == GameRole.CUPID), None)
        assert cupid_role is not None
        assert cupid_role.is_cupid is True

    @patch('app.services.game_flow_service.load_game')
    @patch('app.services.game_flow_service.save_game')
    def test_assign_roles_valid_game_15_players(self, mock_save, mock_load):
        """Test con 15 jugadores (caso medio)"""
        # Arrange
        creator_id = str(uuid.uuid4())
        game = self.create_mock_game(15, creator_id)
        mock_load.return_value = game

        # Act
        result = assign_roles(game.id, creator_id, is_admin=False)

        # Assert
        assert result is not None
        assert len(result.roles) == 15
        
        # Verificar número de hombres lobo (15 // 3 = 5)
        warewolf_count = sum(1 for role_info in result.roles.values() 
                           if role_info.role == GameRole.WAREWOLF)
        assert warewolf_count == 5
        
        # Verificar distribución total de roles
        roles_list = [role_info.role for role_info in result.roles.values()]
        total_special = roles_list.count(GameRole.SEER) + roles_list.count(GameRole.WITCH) + \
                       roles_list.count(GameRole.HUNTER) + roles_list.count(GameRole.CUPID)
        villager_count = roles_list.count(GameRole.VILLAGER)
        
        # 15 total - 5 lobos - 4 especiales = 6 aldeanos
        assert total_special == 4
        assert villager_count == 6

    @patch('app.services.game_flow_service.load_game')
    @patch('app.services.game_flow_service.save_game')
    def test_assign_roles_valid_game_18_players(self, mock_save, mock_load):
        """Test con 18 jugadores (máximo permitido)"""
        # Arrange
        creator_id = str(uuid.uuid4())
        game = self.create_mock_game(18, creator_id)
        mock_load.return_value = game

        # Act
        result = assign_roles(game.id, creator_id, is_admin=False)

        # Assert
        assert result is not None
        assert len(result.roles) == 18
        
        # Verificar número de hombres lobo (18 // 3 = 6)
        warewolf_count = sum(1 for role_info in result.roles.values() 
                           if role_info.role == GameRole.WAREWOLF)
        assert warewolf_count == 6
        
        # 18 total - 6 lobos - 4 especiales = 8 aldeanos
        villager_count = sum(1 for role_info in result.roles.values() 
                           if role_info.role == GameRole.VILLAGER)
        assert villager_count == 8

    @patch('app.services.game_flow_service.load_game')
    def test_assign_roles_insufficient_players(self, mock_load):
        """Test con menos de 10 jugadores (debe fallar)"""
        # Arrange
        creator_id = str(uuid.uuid4())
        game = self.create_mock_game(9, creator_id)  # Menos del mínimo
        mock_load.return_value = game

        # Act
        result = assign_roles(game.id, creator_id, is_admin=False)

        # Assert
        assert result is None

    @patch('app.services.game_flow_service.load_game')
    def test_assign_roles_too_many_players(self, mock_load):
        """Test con más de 18 jugadores (debe fallar)"""
        # Arrange
        creator_id = str(uuid.uuid4())
        game = self.create_mock_game(19, creator_id)  # Más del máximo
        mock_load.return_value = game

        # Act
        result = assign_roles(game.id, creator_id, is_admin=False)

        # Assert
        assert result is None

    @patch('app.services.game_flow_service.load_game')
    def test_assign_roles_game_not_found(self, mock_load):
        """Test cuando la partida no existe"""
        # Arrange
        mock_load.return_value = None

        # Act
        result = assign_roles("nonexistent_id", "user_id", is_admin=False)

        # Assert
        assert result is None

    @patch('app.services.game_flow_service.load_game')
    def test_assign_roles_unauthorized_user(self, mock_load):
        """Test cuando el usuario no es el creador ni admin"""
        # Arrange
        creator_id = str(uuid.uuid4())
        unauthorized_user_id = str(uuid.uuid4())
        game = self.create_mock_game(10, creator_id)
        mock_load.return_value = game

        # Act
        result = assign_roles(game.id, unauthorized_user_id, is_admin=False)

        # Assert
        assert result is None

    @patch('app.services.game_flow_service.load_game')
    @patch('app.services.game_flow_service.save_game')
    def test_assign_roles_admin_can_assign(self, mock_save, mock_load):
        """Test que un admin puede asignar roles aunque no sea el creador"""
        # Arrange
        creator_id = str(uuid.uuid4())
        admin_id = str(uuid.uuid4())
        game = self.create_mock_game(10, creator_id)
        mock_load.return_value = game

        # Act
        result = assign_roles(game.id, admin_id, is_admin=True)

        # Assert
        assert result is not None
        assert result.status == GameStatus.STARTED

    @patch('app.services.game_flow_service.load_game')
    def test_assign_roles_game_already_started(self, mock_load):
        """Test cuando la partida ya ha comenzado"""
        # Arrange
        creator_id = str(uuid.uuid4())
        game = self.create_mock_game(10, creator_id)
        game.status = GameStatus.STARTED  # Ya iniciada
        mock_load.return_value = game

        # Act
        result = assign_roles(game.id, creator_id, is_admin=False)

        # Assert
        assert result is None

    @patch('app.services.game_flow_service.load_game')
    @patch('app.services.game_flow_service.save_game')
    def test_assign_roles_all_players_get_roles(self, mock_save, mock_load):
        """Test que todos los jugadores reciben exactamente un rol"""
        # Arrange
        creator_id = str(uuid.uuid4())
        game = self.create_mock_game(12, creator_id)
        mock_load.return_value = game

        # Act
        result = assign_roles(game.id, creator_id, is_admin=False)

        # Assert
        assert result is not None
        assert len(result.roles) == len(result.players)
        
        # Verificar que todos los jugadores tienen un rol asignado
        player_ids = set(result.players)  # Ya son IDs, no objetos
        role_player_ids = set(result.roles.keys())
        assert player_ids == role_player_ids
        
        # Verificar que todos los roles tienen propiedades válidas
        for role_info in result.roles.values():
            assert role_info.is_alive is True
            assert role_info.is_revealed is False
            assert role_info.role in [
                GameRole.WAREWOLF, GameRole.VILLAGER, GameRole.SEER,
                GameRole.WITCH, GameRole.HUNTER, GameRole.CUPID
            ]

    @patch('app.services.game_flow_service.load_game')
    @patch('app.services.game_flow_service.save_game')
    @patch('app.services.game_flow_service.random.shuffle')
    def test_assign_roles_randomization(self, mock_shuffle, mock_save, mock_load):
        """Test que los roles se mezclan aleatoriamente"""
        # Arrange
        creator_id = str(uuid.uuid4())
        game = self.create_mock_game(10, creator_id)
        mock_load.return_value = game

        # Act
        assign_roles(game.id, creator_id, is_admin=False)

        # Assert
        # Verificar que se llamó shuffle para mezclar roles
        mock_shuffle.assert_called_once()

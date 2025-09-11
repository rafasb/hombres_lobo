"""
Tests unitarios para GameResponsesService.
Valida que los servicios construyan correctamente las respuestas públicas.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from app.models.game_responses import GameResponse, PublicPlayerInfo, GameStateUpdateResponse
from app.models.game_and_player import Game, GameStatus, PlayerInfo, Roles
from app.models.user import User, UserStatus, UserAccessRole
from app.services.game_responses_service import GameResponsesService


class TestGameResponsesService:
    """Tests para el servicio GameResponsesService."""
    
    def setup_method(self):
        """Configuración inicial para cada test."""
        # Crear usuarios de prueba
        self.user1 = User(
            id="player_1",
            username="LoboFeroz",
            email="lobo@test.com",
            role=UserAccessRole.PLAYER,
            status=UserStatus.IN_GAME,
            hashed_password="hash123",
            game_id="game_1"
        )
        
        self.user2 = User(
            id="player_2",
            username="AldeanaAstuta",
            email="aldeana@test.com",
            role=UserAccessRole.PLAYER,
            status=UserStatus.CONNECTED,
            hashed_password="hash456"
        )
        
        self.user3 = User(
            id="player_3",
            username="VidenteSabio",
            email="vidente@test.com",
            role=UserAccessRole.PLAYER,
            status=UserStatus.DISCONNECTED,
            hashed_password="hash789"
        )
        
        # Crear información de jugadores
        self.player_info1 = PlayerInfo(
            role=Roles.WAREWOLF,
            player_id="player_1",
            is_alive=True
        )
        
        self.player_info2 = PlayerInfo(
            role=Roles.VILLAGER,
            player_id="player_2",
            is_alive=True
        )
        
        self.player_info3 = PlayerInfo(
            role=Roles.SEER,
            player_id="player_3",
            is_alive=False
        )
        
        # Crear partida de prueba
        self.game = Game(
            id="game_1",
            name="Partida de Prueba",
            creator_id="player_1",
            max_players=8,
            player_ids=["player_1", "player_2", "player_3"],
            players={
                "player_1": self.player_info1,
                "player_2": self.player_info2,
                "player_3": self.player_info3
            },
            status=GameStatus.NIGHT,
            current_round=2,
            is_first_night=False,
            connected_players=["player_1", "player_2"],
            eliminated_players=["player_3"]
        )
        
        # Diccionario de usuarios
        self.users_dict = {
            "player_1": self.user1,
            "player_2": self.user2,
            "player_3": self.user3
        }
    
    def test_build_public_player_info(self):
        """Test para construir información pública de un jugador."""
        public_player = GameResponsesService.build_public_player_info(
            "player_1", self.user1, self.game
        )
        
        assert isinstance(public_player, PublicPlayerInfo)
        assert public_player.player_id == "player_1"
        assert public_player.username == "LoboFeroz"
        assert public_player.is_alive
        assert public_player.is_connected
        assert public_player.user_status == UserStatus.IN_GAME
    
    def test_build_public_player_info_disconnected(self):
        """Test para jugador desconectado y eliminado."""
        public_player = GameResponsesService.build_public_player_info(
            "player_3", self.user3, self.game
        )
        
        assert public_player.player_id == "player_3"
        assert public_player.username == "VidenteSabio"
        assert not public_player.is_alive
        assert not public_player.is_connected
        assert public_player.user_status == UserStatus.DISCONNECTED
    
    def test_build_public_players_list(self):
        """Test para construir lista de jugadores públicos."""
        public_players = GameResponsesService.build_public_players_list(
            self.game, self.users_dict
        )
        
        assert len(public_players) == 3
        assert all(isinstance(p, PublicPlayerInfo) for p in public_players)
        
        # Verificar que todos los jugadores están incluidos
        player_ids = [p.player_id for p in public_players]
        assert "player_1" in player_ids
        assert "player_2" in player_ids
        assert "player_3" in player_ids
    
    def test_build_game_response(self):
        """Test para construir respuesta completa del juego."""
        game_response = GameResponsesService.build_game_response(
            self.game, self.users_dict
        )
        
        assert isinstance(game_response, GameResponse)
        assert game_response.game_id == "game_1"
        assert game_response.name == "Partida de Prueba"
        assert game_response.creator_id == "player_1"
        assert game_response.creator_name == "LoboFeroz"
        assert game_response.status == GameStatus.NIGHT
        assert game_response.current_round == 2
        assert not game_response.is_first_night
        assert game_response.max_players == 8
        assert game_response.current_players == 3
        assert len(game_response.players) == 3
        assert game_response.eliminated_players == ["player_3"]
        assert game_response.connected_players_count == 2
        assert game_response.success
        assert game_response.message == "Game data retrieved successfully"
    
    def test_build_game_response_unknown_creator(self):
        """Test para partida con creador desconocido."""
        # Crear partida con creador que no está en users_dict
        game = Game(
            id="game_2",
            name="Partida Sin Creador",
            creator_id="unknown_user",
            max_players=4,
            player_ids=["player_1"],
            status=GameStatus.WAITING
        )
        
        game_response = GameResponsesService.build_game_response(
            game, self.users_dict
        )
        
        assert game_response.creator_name == "Desconocido"
    
    def test_build_game_state_update(self):
        """Test para construir actualización de estado."""
        state_update = GameResponsesService.build_game_state_update(
            self.game, self.users_dict, "test_update"
        )
        
        assert isinstance(state_update, GameStateUpdateResponse)
        assert state_update.game_id == "game_1"
        assert state_update.status == GameStatus.NIGHT
        assert state_update.current_round == 2
        assert state_update.current_players == 3
        assert state_update.connected_players_count == 2
        assert len(state_update.players) == 3
        assert state_update.eliminated_players == ["player_3"]
        assert state_update.update_type == "test_update"
        assert isinstance(state_update.timestamp, datetime)
    
    @patch('app.services.game_responses_service.get_game')
    @patch('app.services.game_responses_service.UserService.get_user')
    def test_get_game_response_by_id(self, mock_get_user, mock_get_game):
        """Test para obtener respuesta de juego por ID."""
        # Configurar mocks
        mock_get_game.return_value = self.game
        mock_get_user.side_effect = lambda user_id: self.users_dict.get(user_id)
        
        game_response = GameResponsesService.get_game_response_by_id("game_1")
        
        assert game_response is not None
        assert isinstance(game_response, GameResponse)
        assert game_response.game_id == "game_1"
        
        # Verificar que se llamaron los métodos correctos
        mock_get_game.assert_called_once_with("game_1")
        assert mock_get_user.call_count >= 3  # Al menos una vez por jugador
    
    @patch('app.services.game_responses_service.get_game')
    def test_get_game_response_by_id_not_found(self, mock_get_game):
        """Test para partida no encontrada."""
        mock_get_game.return_value = None
        
        game_response = GameResponsesService.get_game_response_by_id("nonexistent")
        
        assert game_response is None
    
    @patch('app.services.game_responses_service.get_game')
    @patch('app.services.game_responses_service.UserService.get_user')
    def test_get_game_state_update_by_id(self, mock_get_user, mock_get_game):
        """Test para obtener actualización de estado por ID."""
        mock_get_game.return_value = self.game
        mock_get_user.side_effect = lambda user_id: self.users_dict.get(user_id)
        
        state_update = GameResponsesService.get_game_state_update_by_id(
            "game_1", "custom_update"
        )
        
        assert state_update is not None
        assert isinstance(state_update, GameStateUpdateResponse)
        assert state_update.update_type == "custom_update"
    
    @patch('app.services.game_responses_service.GameResponsesService.get_game_state_update_by_id')
    def test_create_player_connection_update(self, mock_get_update):
        """Test para crear actualización de conexión de jugador."""
        mock_get_update.return_value = Mock(spec=GameStateUpdateResponse)
        
        # Test para conexión
        GameResponsesService.create_player_connection_update(
            "game_1", "player_1", True
        )
        mock_get_update.assert_called_with("game_1", "player_connected")
        
        # Test para desconexión
        GameResponsesService.create_player_connection_update(
            "game_1", "player_1", False
        )
        mock_get_update.assert_called_with("game_1", "player_disconnected")
    
    @patch('app.services.game_responses_service.GameResponsesService.get_game_state_update_by_id')
    def test_create_phase_change_update(self, mock_get_update):
        """Test para crear actualización de cambio de fase."""
        mock_get_update.return_value = Mock(spec=GameStateUpdateResponse)
        
        GameResponsesService.create_phase_change_update("game_1", GameStatus.DAY)
        
        mock_get_update.assert_called_with("game_1", "phase_change_to_day")
    
    @patch('app.services.game_responses_service.GameResponsesService.get_game_state_update_by_id')
    def test_create_player_elimination_update(self, mock_get_update):
        """Test para crear actualización de eliminación de jugador."""
        mock_get_update.return_value = Mock(spec=GameStateUpdateResponse)
        
        GameResponsesService.create_player_elimination_update("game_1", "player_3")
        
        mock_get_update.assert_called_with("game_1", "player_eliminated")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

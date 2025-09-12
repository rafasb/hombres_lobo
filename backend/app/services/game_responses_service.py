"""
Servicio para generar respuestas de partida con información pública.
Este módulo se encarga de construir objetos GameResponse, PublicPlayerInfo y 
GameStateUpdateResponse a partir de los datos del juego y usuarios.
"""

from typing import Dict, List, Optional
from datetime import datetime, UTC

from app.models.game_responses import GameResponse, PublicPlayerInfo, GameStateUpdateResponse
from app.models.game_and_player import Game, GameStatus
from app.models.user import User
from app.services.game_service import get_game
from app.services.user_service import UserService


class GameResponsesService:
    """Servicio para generar respuestas públicas de partidas."""
    
    @staticmethod
    def build_public_player_info(
        player_id: str, 
        user: User, 
        game: Game
    ) -> PublicPlayerInfo:
        """
        Construye información pública de un jugador específico.
        
        Args:
            player_id: ID del jugador
            user: Objeto User con información del usuario
            game: Objeto Game con información de la partida
            
        Returns:
            PublicPlayerInfo con datos públicos del jugador
        """
        # Obtener información del jugador en la partida
        player_info = game.get_player_state(player_id)
        is_alive = player_info.is_alive if player_info else True
        
        return PublicPlayerInfo(
            player_id=player_id,
            username=user.username,
            is_alive=is_alive,
            user_status=user.status
        )
    
    @staticmethod
    def build_public_players_list(
        game: Game, 
        users_dict: Dict[str, User]
    ) -> List[PublicPlayerInfo]:
        """
        Construye una lista de información pública de todos los jugadores.
        
        Args:
            game: Objeto Game con información de la partida
            users_dict: Diccionario {user_id: User} con información de usuarios
            
        Returns:
            Lista de PublicPlayerInfo para todos los jugadores
        """
        public_players = []
        
        for player_id in game.player_ids:
            if player_id in users_dict:
                user = users_dict[player_id]
                public_player = GameResponsesService.build_public_player_info(
                    player_id, user, game
                )
                public_players.append(public_player)
        
        return public_players
    
    @staticmethod
    def build_game_response(
        game: Game, 
        users_dict: Dict[str, User],
        success: bool = True,
        message: str = "Game data retrieved successfully"
    ) -> GameResponse:
        """
        Construye una respuesta completa del estado de la partida.
        
        Args:
            game: Objeto Game con información de la partida
            users_dict: Diccionario {user_id: User} con información de usuarios
            success: Indica si la operación fue exitosa
            message: Mensaje descriptivo de la respuesta
            
        Returns:
            GameResponse con toda la información pública de la partida
        """
        # Construir lista de jugadores públicos
        public_players = GameResponsesService.build_public_players_list(game, users_dict)
        
        # Obtener nombre del creador
        creator_user = users_dict.get(game.creator_id)
        creator_name = creator_user.username if creator_user else "Desconocido"
        
        return GameResponse(
            game_id=game.id,
            name=game.name,
            creator_id=game.creator_id,
            creator_name=creator_name,
            status=game.status,
            current_round=game.current_round,
            is_first_night=game.is_first_night,
            max_players=game.max_players,
            current_players=len(game.player_ids),
            players=public_players,
            eliminated_players=game.eliminated_players.copy(),
            connected_players_count=len(game.connected_players),
            created_at=game.created_at,
            success=success,
            message=message
        )
    
    @staticmethod
    def build_game_state_update(
        game: Game, 
        users_dict: Dict[str, User],
        update_type: str = "game_state_update"
    ) -> GameStateUpdateResponse:
        """
        Construye una respuesta simplificada para actualizaciones de estado.
        Ideal para mensajes WebSocket.
        
        Args:
            game: Objeto Game con información de la partida
            users_dict: Diccionario {user_id: User} con información de usuarios
            update_type: Tipo de actualización (game_state_update, phase_change, etc.)
            
        Returns:
            GameStateUpdateResponse con datos esenciales para el frontend
        """
        # Construir lista de jugadores públicos
        public_players = GameResponsesService.build_public_players_list(game, users_dict)
        
        return GameStateUpdateResponse(
            game_id=game.id,
            status=game.status,
            current_round=game.current_round,
            current_players=len(game.player_ids),
            connected_players_count=len(game.connected_players),
            players=public_players,
            eliminated_players=game.eliminated_players.copy(),
            update_type=update_type,
            timestamp=datetime.now(UTC)
        )
    
    @staticmethod
    def get_game_response_by_id(
        game_id: str,
        success: bool = True,
        message: str = "Game data retrieved successfully"
    ) -> Optional[GameResponse]:
        """
        Obtiene una respuesta completa de partida por su ID.
        
        Args:
            game_id: ID de la partida
            success: Indica si la operación fue exitosa
            message: Mensaje descriptivo de la respuesta
            
        Returns:
            GameResponse si la partida existe, None en caso contrario
        """
        # Cargar la partida
        game = get_game(game_id)
        if not game:
            return None
        
        # Cargar información de todos los usuarios de la partida
        users_dict = {}
        for player_id in game.player_ids:
            user = UserService.get_user(player_id)
            if user:
                users_dict[player_id] = user
        
        # Agregar el creador si no está en la lista de jugadores
        if game.creator_id not in users_dict:
            creator = UserService.get_user(game.creator_id)
            if creator:
                users_dict[game.creator_id] = creator
        
        return GameResponsesService.build_game_response(game, users_dict, success, message)
    
    @staticmethod
    def get_game_state_update_by_id(
        game_id: str,
        update_type: str = "game_state_update"
    ) -> Optional[GameStateUpdateResponse]:
        """
        Obtiene una actualización de estado de partida por su ID.
        
        Args:
            game_id: ID de la partida
            update_type: Tipo de actualización
            
        Returns:
            GameStateUpdateResponse si la partida existe, None en caso contrario
        """
        # Cargar la partida
        game = get_game(game_id)
        if not game:
            return None
        
        # Cargar información de todos los usuarios de la partida
        users_dict = {}
        for player_id in game.player_ids:
            user = UserService.get_user(player_id)
            if user:
                users_dict[player_id] = user
        
        return GameResponsesService.build_game_state_update(game, users_dict, update_type)
    
    @staticmethod
    def create_player_connection_update(
        game_id: str,
        player_id: str,
        is_connected: bool
    ) -> Optional[GameStateUpdateResponse]:
        """
        Crea una actualización específica para cambios de conexión de jugadores.
        
        Args:
            game_id: ID de la partida
            player_id: ID del jugador que cambió su estado de conexión
            is_connected: True si se conectó, False si se desconectó
            
        Returns:
            GameStateUpdateResponse con la actualización de conexión
        """
        update_type = "player_connected" if is_connected else "player_disconnected"
        return GameResponsesService.get_game_state_update_by_id(game_id, update_type)
    
    @staticmethod
    def create_phase_change_update(
        game_id: str,
        new_phase: GameStatus
    ) -> Optional[GameStateUpdateResponse]:
        """
        Crea una actualización específica para cambios de fase del juego.
        
        Args:
            game_id: ID de la partida
            new_phase: Nueva fase del juego
            
        Returns:
            GameStateUpdateResponse con la actualización de fase
        """
        return GameResponsesService.get_game_state_update_by_id(
            game_id, 
            f"phase_change_to_{new_phase.value}"
        )
    
    @staticmethod
    def create_player_elimination_update(
        game_id: str,
        eliminated_player_id: str
    ) -> Optional[GameStateUpdateResponse]:
        """
        Crea una actualización específica para eliminación de jugadores.
        
        Args:
            game_id: ID de la partida
            eliminated_player_id: ID del jugador eliminado
            
        Returns:
            GameStateUpdateResponse con la actualización de eliminación
        """
        return GameResponsesService.get_game_state_update_by_id(
            game_id, 
            "player_eliminated"
        )

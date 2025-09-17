"""
Modelos de respuesta específicos para los endpoints de gestión de partidas.
Define las estructuras de datos para las respuestas de la API de games.

Clases principales:
- PublicPlayerInfo: Información pública de un jugador (sin datos sensibles como rol)
- GameResponse: Respuesta completa del estado de una partida
- GameStateUpdateResponse: Respuesta simplificada para actualizaciones WebSocket

Estas clases están diseñadas para compartir información del juego con todos los 
jugadores sin revelar datos sensibles como roles, acciones nocturnas, etc.
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models.game_and_player import Game, GameStatus
from app.models.user import UserStatus


class PublicPlayerInfo(BaseModel):
    """Información pública de un jugador que puede ser compartida con todos los participantes."""
    player_id: str
    username: str
    is_alive: bool
    # is_connected: bool
    user_status: UserStatus  # connected, disconnected, in_game
    

class GameResponse(BaseModel):
    """
    Respuesta completa del estado de una partida con información pública 
    que puede ser compartida con todos los jugadores.
    """
    # Información básica de la partida
    game_id: str
    name: str
    creator_id: str
    creator_name: str
    
    # Estado actual de la partida
    status: GameStatus
    current_round: int
    is_first_night: bool
    
    # Información de jugadores
    max_players: int
    current_players: int
    players: List[PublicPlayerInfo]
    defeated_players_ids: List[str]  # IDs de jugadores eliminados
    connected_players_count: int  # Jugadores en la partida
    
    # Información temporal
    created_at: Optional[datetime] = None
    
    # Metadatos
    success: bool = True
    message: str = "Game data retrieved successfully"


class GameStateUpdateResponse(BaseModel):
    """
    Respuesta simplificada para actualizaciones de estado del juego via WebSocket.
    Incluye solo los campos que cambian frecuentemente.
    """
    game_id: str
    status: GameStatus
    current_round: int
    current_players: int
    connected_players_count: int
    players: List[PublicPlayerInfo]
    eliminated_players: List[str]
    
    # Tipo de actualización para el frontend
    update_type: str = "game_state_update"
    timestamp: Optional[datetime] = None


class GameActionResponse(BaseModel):
    """Respuesta genérica para acciones sobre partidas."""
    success: bool
    message: str


class GameJoinResponse(BaseModel):
    """Respuesta para cuando un jugador se une a una partida."""
    success: bool
    message: str
    game_id: str
    current_players: int
    max_players: int


class GameLeaveResponse(BaseModel):
    """Respuesta para cuando un jugador abandona una partida."""
    success: bool
    message: str
    game_id: str
    remaining_players: int


class GameDeleteResponse(BaseModel):
    """Respuesta para cuando se elimina una partida."""
    success: bool
    message: str
    deleted_game_id: str


class GameListResponse(BaseModel):
    """Respuesta para el listado de partidas con versión 2."""
    class GameSummary(BaseModel):
        id: str
        name: str
        creator_name: str
        creator_id: str
        created_at: str | None = None
        current_round: int | None = None
        current_players: int
        max_players: int
        status: str
        player_ids: List[str] | None = None  # Opcional, para futuras mejoras
    success: bool
    games: List[GameSummary]
    total_games: int


# class GameCreateResponse(BaseModel):
#     """Respuesta para la creación de una partida."""
#     success: bool
#     message: str
#     game: Game


class GameUpdateResponse(BaseModel):
    """Respuesta para la actualización de parámetros de una partida."""
    # TODO: Revisar si debe debe devolver un objeto Game o solo los campos accesibles a 
    # los jugadores (sin roles, acciones nocturnas, etc.)
    # Quizá sea conveniente definir un modelo GamePublic o similar.
    success: bool
    message: str
    game: Game
    updated_fields: List[str]


class GameStatusUpdateResponse(BaseModel):
    """Respuesta para la actualización del estado de una partida."""
    # TODO: Revisar si debe debe devolver un objeto Game o solo los campos accesibles a
    # los jugadores (sin roles, acciones nocturnas, etc.)
    # Quizá sea conveniente definir un modelo GamePublic o similar.
    # Posiblemente redundante con la clase GameUpdateResponse
    success: bool
    message: str
    game: Game
    previous_status: str
    new_status: str


class GameRoleAssignmentResponse(BaseModel):
    """Respuesta para la asignación de roles en una partida."""
    # TODO: Revisar si debe debe devolver un objeto Game o solo los campos accesibles a
    # los jugadores (sin roles, acciones nocturnas, etc.)
    # Quizá sea conveniente definir un modelo GamePublic o similar.
    # Posiblemente redundante con la clase GameUpdateResponse
    success: bool
    message: str
    game: Game
    assigned_roles_count: int
    players_with_roles: int


class GameGetResponse(BaseModel):
    """Respuesta para obtener información de una partida específica."""
    # TODO: Revisar si debe debe devolver un objeto Game o solo los campos accesibles a
    # los jugadores (sin roles, acciones nocturnas, etc.)
    # Quizá sea conveniente definir un modelo GamePublic o similar.
    success: bool
    message: str
    game: Game

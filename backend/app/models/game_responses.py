"""
Modelos de respuesta específicos para los endpoints de gestión de partidas.
Define las estructuras de datos para las respuestas de la API de games.
"""

from pydantic import BaseModel
from typing import List
from app.models.game_and_roles import GameResponse


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
    """Respuesta para el listado de partidas."""
    success: bool
    message: str
    games: List[GameResponse]
    total_games: int


class GameCreateResponse(BaseModel):
    """Respuesta para la creación de una partida."""
    success: bool
    message: str
    game: GameResponse


class GameUpdateResponse(BaseModel):
    """Respuesta para la actualización de parámetros de una partida."""
    success: bool
    message: str
    game: GameResponse
    updated_fields: List[str]


class GameStatusUpdateResponse(BaseModel):
    """Respuesta para la actualización del estado de una partida."""
    success: bool
    message: str
    game: GameResponse
    previous_status: str
    new_status: str


class GameRoleAssignmentResponse(BaseModel):
    """Respuesta para la asignación de roles en una partida."""
    success: bool
    message: str
    game: GameResponse
    assigned_roles_count: int
    players_with_roles: int


class GameGetResponse(BaseModel):
    """Respuesta para obtener información de una partida específica."""
    success: bool
    message: str
    game: GameResponse

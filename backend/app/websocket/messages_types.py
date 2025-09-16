"""
Modelos para mensajes WebSocket
Define los tipos de mensajes y su estructura
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, List
from datetime import datetime
from enum import Enum
from app.models.game_and_player import PlayerInfo
from app.services.voting_service import VoteType
from app.services.game_state_service import GamePhase

class MessageType(str, Enum):
    # Estados de usuario
    PLAYER_STATUS_CHANGED = "user_status_changed"
    
    # Comandos de juego
    RESTART_GAME = "restart_game"
    GAME_STATUS = "game_status"
    
    # Fases del juego
    PHASE_CHANGED = "phase_changed"
    PHASE_TIMER = "phase_timer"
    GAME_STARTED = "game_started"
    GAME_ENDED = "game_ended"
    
    # Votaciones
    VOTE_CAST = "vote_cast"
    VOTING_STARTED = "voting_started"
    VOTING_ENDED = "voting_ended"
    VOTING_RESULTS = "voting_results"
    
    # Acciones de roles
    ROLE_ACTION = "role_action"
    NIGHT_ACTION = "night_action"
    
    # Eventos del juego
    PLAYER_ELIMINATED = "player_eliminated"
    PLAYER_ROLE_REVEALED = "player_role_revealed"
    
    # Sistema
    HEARTBEAT = "heartbeat"
    ERROR = "error"
    SUCCESS = "success"
    SYSTEM_MESSAGE = "system_message"
    
    # Estados de conexión
    GAME_CONNECTION_STATE = "game_connection_state"
    PLAYERS_STATUS_UPDATE = "players_status_update"
    USER_CONNECTION_STATUS = "user_connection_status"
    GAME_RESTARTED = "game_restarted"

class ErrorCode(str, Enum):
    INVALID_MESSAGE = "INVALID_MESSAGE"
    UNKNOWN_MESSAGE_TYPE = "UNKNOWN_MESSAGE_TYPE"
    INVALID_MESSAGE_TYPE = "INVALID_MESSAGE_TYPE"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    GAME_NOT_FOUND = "GAME_NOT_FOUND"
    GAME_NOT_STARTED = "GAME_NOT_STARTED"
    USER_NOT_IN_GAME = "USER_NOT_IN_GAME"
    NOT_AUTHORIZED = "NOT_AUTHORIZED"
    INVALID_ACTION = "INVALID_ACTION"
    INVALID_PHASE = "INVALID_PHASE"
    VOTE_NOT_ALLOWED = "VOTE_NOT_ALLOWED"
    PHASE_CHANGE_FAILED = "PHASE_CHANGE_FAILED"
    PHASE_FORCE_FAILED = "PHASE_FORCE_FAILED"
    PLAYER_NOT_FOUND = "PLAYER_NOT_FOUND"
    PLAYER_ALREADY_ELIMINATED = "PLAYER_ALREADY_ELIMINATED"
    ROLE_ACTION_NOT_ALLOWED = "ROLE_ACTION_NOT_ALLOWED"
    JOIN_ERROR = "JOIN_ERROR"
    START_GAME_ERROR = "START_GAME_ERROR"
    RESTART_GAME_ERROR = "RESTART_GAME_ERROR"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    STATUS_ERROR = "STATUS_ERROR"
    MISSING_FIELD = "MISSING_FIELD"
    INVALID_CONNECTION = "INVALID_CONNECTION"
    INVALID_USER = "INVALID_USER"
    INVALID_STATUS = "INVALID_STATUS"
    UPDATE_FAILED = "UPDATE_FAILED"

class SystemMessageType(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CONNECTED_TO_GAME = "connected_to_game"
    DISCONNECTED_FROM_GAME = "disconnected_from_game"
    PLAYER_JOINED = "player_joined"
    GAME_STARTED = "game_started"
    GAME_ENDED = "game_ended"
    PHASE_CHANGED = "phase_changed"
    VOTING_STARTED = "voting_started"
    VOTING_ENDED = "voting_ended"
    PLAYER_ELIMINATED = "player_eliminated"

class BaseWebSocketMessage(BaseModel):
    """Clase base para todos los mensajes WebSocket"""
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class WebSocketMessageV2(BaseWebSocketMessage):
    """Mensaje base para WebSocket versión 2"""
    type: MessageType           # Tipo de mensaje
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Any # Objeto con el contenido del mensaje (específico por tipo de mensaje)
    model_config = ConfigDict(extra="allow", from_attributes=True)  # Permitir campos adicionales

class UserIdName(BaseModel):
    id: str = Field(default="")
    name: str = Field(default="")

class WsMessageError(WebSocketMessageV2):
    """Mensaje de error websocket version 2"""
    type: MessageType = MessageType.ERROR
    error_code: ErrorCode = ErrorCode.INTERNAL_ERROR
    data: str = "Error interno del servidor"

class WsMessageSuccess(WebSocketMessageV2):
    """Mensaje de éxito websocket version 2"""
    type: MessageType = MessageType.SUCCESS
    data: str

class WsPhaseChangedMessage(WebSocketMessageV2):
    """Mensaje de cambio de fase websocket version 2"""
    type: MessageType = MessageType.PHASE_CHANGED
    data: str  # Nombre de la fase
    duration: int  # Duración en segundos

class WsTimerMessage(WebSocketMessageV2):
    """Mensaje de timer websocket version 2"""
    type: MessageType = MessageType.PHASE_TIMER
    phase: str
    data: int  # Tiempo restante en segundos
    game_id: str | None = None
    user_id: str | None = None

class WsVotingStartedMessage(WebSocketMessageV2):
    """Mensaje de inicio de votación websocket version 2"""
    type: MessageType = MessageType.VOTING_STARTED
    data: VoteType
    duration: int  # Duración en segundos
    game_id: str
    eligible_voters: List[str]  # IDs de jugadores que pueden votar
    vote_targets: List[str]     # IDs de jugadores por los que se puede votar

class WsVotingEndedMessage(WebSocketMessageV2):
    """Mensaje de fin de votación websocket version 2"""
    type: MessageType = MessageType.VOTING_ENDED
    data: VoteType
    game_id: str
    results: Dict[str, int]  # target_id -> vote_count
    eliminated_player: str | None = None
    is_tie: bool = False

class WsVoteMessage(WebSocketMessageV2):
    """Mensaje de voto websocket version 2"""
    type: MessageType = MessageType.VOTE_CAST
    voter_id: str
    target_id: str
    vote_type: str  # day_vote, sheriff_vote, etc
    data: str = ""  # Mensaje opcional

class WsMessageGameStatus(WebSocketMessageV2):
    """Mensaje de estado de juego websocket version 2"""
    type: MessageType = MessageType.GAME_STATUS
    data: str | None = None # Mensaje de estado
    game_id: str
    phase: GamePhase
    players: List[PlayerInfo]
    connected_players: List[str]  # IDs de jugadores conectados
    living_players: List[str]    # IDs de jugadores vivos
    dead_players: List[str]      # IDs de jugadores muertos
    is_first_night: bool | None = None
    time_remaining: int | None = None  # Segundos restantes en la fase actual

class WsSystemMessage(WebSocketMessageV2):
    """Mensaje del sistema websocket version 2"""
    type: MessageType = MessageType.SYSTEM_MESSAGE
    data: str  # Mensaje del sistema
    message_key: SystemMessageType | None = None  # Para i18n
    params: Dict[str, Any] = {}

class WsRoleActionMessage(WebSocketMessageV2):
    """Mensaje de acción de rol websocket version 2"""
    type: MessageType = MessageType.ROLE_ACTION
    actor_id: str
    action: str  # see, heal, poison, shoot, etc
    target_id: str | None = None
    data: str = ""  # Mensaje adicional

class WsPlayerEliminatedMessage(WebSocketMessageV2):
    """Mensaje de jugador eliminado websocket version 2"""
    type: MessageType = MessageType.PLAYER_ELIMINATED
    player_id: str
    player_name: str
    role: str | None = None
    elimination_type: str  # vote, night_kill, poison, etc
    data: str = ""

class WsGameStartedMessage(WebSocketMessageV2):
    """Mensaje de juego iniciado websocket version 2"""
    type: MessageType = MessageType.GAME_STARTED
    players: List[Dict[str, str]]  # List of {"id": user_id, "name": username}
    roles_assigned: bool = True
    data: str = "Game has started"

class WsGameEndedMessage(WebSocketMessageV2):
    """Mensaje de juego terminado websocket version 2"""
    type: MessageType = MessageType.GAME_ENDED
    winning_team: str  # wolves, villagers, lovers, etc
    winners: List[str]  # user_ids
    final_roles: Dict[str, str]  # user_id -> role
    data: str = "Game has ended"

class WsUserStatusChangedMessage(WebSocketMessageV2):
    """Mensaje de cambio de estado de usuario websocket version 2"""
    type: MessageType = MessageType.PLAYER_STATUS_CHANGED
    user_id: str
    old_status: str
    new_status: str
    data: str = ""

class WsGameConnectionStateMessage(WebSocketMessageV2):
    """Mensaje de estado de conexión del juego websocket version 2"""
    type: MessageType = MessageType.GAME_CONNECTION_STATE
    isUserConnected: bool
    isUserInGame: bool
    connectedPlayersCount: int
    totalPlayersCount: int
    playersStatus: List[Dict[str, Any]]
    lastUpdate: datetime = Field(default_factory=datetime.now)
    data: str = ""

class WsPlayersStatusUpdateMessage(WebSocketMessageV2):
    """Mensaje de actualización de estado de jugadores websocket version 2"""
    type: MessageType = MessageType.PLAYERS_STATUS_UPDATE
    playersStatus: List[Dict[str, Any]]
    data: str = ""

class WsUserConnectionStatusMessage(WebSocketMessageV2):
    """Mensaje de estado de conexión de usuario websocket version 2"""
    type: MessageType = MessageType.USER_CONNECTION_STATUS
    isConnected: bool
    isInGame: bool
    data: str = ""

# Tipos de mensajes para validación (actualizados)
MESSAGE_MODELS = {
    MessageType.PLAYER_STATUS_CHANGED: WsUserStatusChangedMessage,
    MessageType.PHASE_CHANGED: WsPhaseChangedMessage,
    MessageType.PHASE_TIMER: WsTimerMessage,
    MessageType.VOTE_CAST: WsVoteMessage,
    MessageType.VOTING_STARTED: WsVotingStartedMessage,
    MessageType.VOTING_ENDED: WsVotingEndedMessage,
    MessageType.SYSTEM_MESSAGE: WsSystemMessage,
    MessageType.ROLE_ACTION: WsRoleActionMessage,
    MessageType.PLAYER_ELIMINATED: WsPlayerEliminatedMessage,
    MessageType.GAME_STARTED: WsGameStartedMessage,
    MessageType.GAME_ENDED: WsGameEndedMessage,
    MessageType.ERROR: WsMessageError,
    MessageType.SUCCESS: WsMessageSuccess,
    MessageType.GAME_CONNECTION_STATE: WsGameConnectionStateMessage,
    MessageType.PLAYERS_STATUS_UPDATE: WsPlayersStatusUpdateMessage,
    MessageType.USER_CONNECTION_STATUS: WsUserConnectionStatusMessage,
    MessageType.GAME_STATUS: WsMessageGameStatus,
}

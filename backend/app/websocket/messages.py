"""
Modelos para mensajes WebSocket
Define los tipos de mensajes y su estructura
"""
from pydantic import BaseModel, Field
from typing import Any, Dict, List
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    # Conexión
    PLAYER_CONNECTED = "player_connected"
    PLAYER_DISCONNECTED = "player_disconnected" 
    PLAYER_LEFT_GAME = "player_left_game"
    
    # Comandos de juego
    JOIN_GAME = "join_game"
    START_GAME = "start_game"
    RESTART_GAME = "restart_game"
    GET_GAME_STATUS = "get_game_status"
    FORCE_NEXT_PHASE = "force_next_phase"
    
    # Comandos de votación
    CAST_VOTE = "cast_vote"
    GET_VOTING_STATUS = "get_voting_status"
    
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
    
    # Chat
    CHAT_MESSAGE = "chat_message"
    SYSTEM_MESSAGE = "system_message"
    
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
    
    # Nuevos tipos para compatibilidad con frontend
    GAME_CONNECTION_STATE = "game_connection_state"
    PLAYERS_STATUS_UPDATE = "players_status_update"
    USER_CONNECTION_STATUS = "user_connection_status"

class BaseWebSocketMessage(BaseModel):
    """Clase base para todos los mensajes WebSocket"""
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class WebSocketMessage(BaseWebSocketMessage):
    """Mensaje base para WebSocket"""
    type: MessageType
    game_id: str | None = None
    user_id: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Dict[str, Any] = {}

class PlayerConnectionMessage(BaseWebSocketMessage):
    """Mensaje de conexión/desconexión de jugador"""
    type: MessageType
    user_id: str
    username: str
    timestamp: datetime = Field(default_factory=datetime.now)

class PhaseChangedMessage(BaseWebSocketMessage):
    """Mensaje de cambio de fase"""
    type: MessageType = MessageType.PHASE_CHANGED
    phase: str  # night, day, voting, trial, execution
    duration: int  # segundos
    timestamp: datetime = Field(default_factory=datetime.now)

class PhaseTimerMessage(BaseWebSocketMessage):
    """Mensaje de timer de fase"""
    type: MessageType = MessageType.PHASE_TIMER
    phase: str
    time_remaining: int  # segundos
    timestamp: datetime = Field(default_factory=datetime.now)

class ForceNextPhaseMessage(BaseWebSocketMessage):
    """Mensaje para forzar cambio a la siguiente fase"""
    type: MessageType = MessageType.FORCE_NEXT_PHASE
    timestamp: datetime = Field(default_factory=datetime.now)

class VoteMessage(BaseWebSocketMessage):
    """Mensaje de voto"""
    type: MessageType = MessageType.VOTE_CAST
    voter_id: str
    target_id: str
    vote_type: str  # day_vote, sheriff_vote, etc
    timestamp: datetime = Field(default_factory=datetime.now)

class VotingResultsMessage(BaseWebSocketMessage):
    """Resultados de votación"""
    type: MessageType = MessageType.VOTING_RESULTS
    vote_type: str
    results: Dict[str, int]  # target_id -> vote_count
    eliminated_player: str | None = None
    is_tie: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)

class ChatMessage(BaseWebSocketMessage):
    """Mensaje de chat"""
    type: MessageType = MessageType.CHAT_MESSAGE
    sender_id: str
    sender_name: str
    message: str
    channel: str  # all, living, dead, wolves
    timestamp: datetime = Field(default_factory=datetime.now)

class SystemMessage(BaseWebSocketMessage):
    """Mensaje del sistema"""
    type: MessageType = MessageType.SYSTEM_MESSAGE
    message: str
    message_key: str | None = None  # Para i18n
    params: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.now)

class RoleActionMessage(BaseWebSocketMessage):
    """Mensaje de acción de rol"""
    type: MessageType = MessageType.ROLE_ACTION
    actor_id: str
    action: str  # see, heal, poison, shoot, etc
    target_id: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)

class PlayerEliminatedMessage(BaseWebSocketMessage):
    """Mensaje de jugador eliminado"""
    type: MessageType = MessageType.PLAYER_ELIMINATED
    player_id: str
    player_name: str
    role: str | None = None
    elimination_type: str  # vote, night_kill, poison, etc
    timestamp: datetime = Field(default_factory=datetime.now)

class GameStartedMessage(BaseWebSocketMessage):
    """Mensaje de juego iniciado"""
    type: MessageType = MessageType.GAME_STARTED
    players: List[Dict[str, Any]]
    roles_assigned: bool = True
    timestamp: datetime = Field(default_factory=datetime.now)

class GameEndedMessage(BaseWebSocketMessage):
    """Mensaje de juego terminado"""
    type: MessageType = MessageType.GAME_ENDED
    winning_team: str  # wolves, villagers, lovers, etc
    winners: List[str]  # user_ids
    final_roles: Dict[str, str]  # user_id -> role
    timestamp: datetime = Field(default_factory=datetime.now)

class ErrorMessage(BaseWebSocketMessage):
    """Mensaje de error"""
    type: MessageType = MessageType.ERROR
    error_code: str
    message: str
    details: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.now)

class SuccessMessage(BaseWebSocketMessage):
    """Mensaje de éxito"""
    type: MessageType = MessageType.SUCCESS
    action: str
    message: str
    data: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.now)

class GameConnectionStateMessage(BaseWebSocketMessage):
    """Mensaje de estado de conexión del juego"""
    type: MessageType = MessageType.GAME_CONNECTION_STATE
    isUserConnected: bool
    isUserInGame: bool
    connectedPlayersCount: int
    totalPlayersCount: int
    playersStatus: List[Dict[str, Any]]
    lastUpdate: datetime = Field(default_factory=datetime.now)

class PlayersStatusUpdateMessage(BaseWebSocketMessage):
    """Mensaje de actualización de estado de jugadores"""
    type: MessageType = MessageType.PLAYERS_STATUS_UPDATE
    playersStatus: List[Dict[str, Any]]
    timestamp: datetime = Field(default_factory=datetime.now)

class UserConnectionStatusMessage(BaseWebSocketMessage):
    """Mensaje de estado de conexión de usuario"""
    type: MessageType = MessageType.USER_CONNECTION_STATUS
    isConnected: bool
    isInGame: bool
    timestamp: datetime = Field(default_factory=datetime.now)

# Tipos de mensajes para validación
MESSAGE_MODELS = {
    MessageType.PLAYER_CONNECTED: PlayerConnectionMessage,
    MessageType.PLAYER_DISCONNECTED: PlayerConnectionMessage,
    MessageType.PHASE_CHANGED: PhaseChangedMessage,
    MessageType.PHASE_TIMER: PhaseTimerMessage,
    MessageType.FORCE_NEXT_PHASE: ForceNextPhaseMessage,
    MessageType.VOTE_CAST: VoteMessage,
    MessageType.VOTING_RESULTS: VotingResultsMessage,
    MessageType.CHAT_MESSAGE: ChatMessage,
    MessageType.SYSTEM_MESSAGE: SystemMessage,
    MessageType.ROLE_ACTION: RoleActionMessage,
    MessageType.PLAYER_ELIMINATED: PlayerEliminatedMessage,
    MessageType.GAME_STARTED: GameStartedMessage,
    MessageType.GAME_ENDED: GameEndedMessage,
    MessageType.ERROR: ErrorMessage,
    MessageType.SUCCESS: SuccessMessage,
    MessageType.GAME_CONNECTION_STATE: GameConnectionStateMessage,
    MessageType.PLAYERS_STATUS_UPDATE: PlayersStatusUpdateMessage,
    MessageType.USER_CONNECTION_STATUS: UserConnectionStatusMessage,
}

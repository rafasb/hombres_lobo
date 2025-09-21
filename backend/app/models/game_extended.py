"""
Modelo Game Extendido para migración temporal
Incluye nuevos campos sin romper la funcionalidad existente
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict
from pydantic import Field
from enum import Enum

from app.models.game_and_player import Game

class GamePhase(str, Enum):
    """Nuevo enum para fases más granulares del juego"""
    WAITING = "waiting"
    STARTING = "starting"
    DAY_DISCUSSION = "day_discussion"
    DAY_VOTING = "day_voting"
    NIGHT_ACTIONS = "night_actions"
    NIGHT_RESOLUTION = "night_resolution"
    GAME_OVER = "game_over"
    PAUSED = "paused"

class GameExtended(Game):
    """
    Versión extendida del modelo Game para migración.
    Incluye nuevos campos que se persistirán en base de datos.
    Mantiene compatibilidad total con Game original.
    """
    
    # 🆕 Gestión de Fases
    current_phase: GamePhase = GamePhase.WAITING
    phase_start_time: Optional[datetime] = None
    phase_duration_seconds: Optional[int] = None
    phase_auto_advance: bool = True
    
    # 🆕 Temporizadores Persistentes (reemplazo de asyncio.create_task)
    next_phase_at: Optional[datetime] = None  # Cuándo avanzar automáticamente
    phase_end_actions: List[str] = Field(default_factory=list)  # Acciones al terminar fase
    
    # 🆕 Estado de Votación
    voting_active: bool = False
    voting_start_time: Optional[datetime] = None
    voting_end_time: Optional[datetime] = None
    voting_type: Optional[str] = None  # "lynch", "sheriff", etc.
    
    # 🆕 Acciones Nocturnas Ampliadas
    pending_night_actions: Dict[str, Dict] = Field(default_factory=dict)
    completed_night_actions: List[str] = Field(default_factory=list)
    night_action_deadline: Optional[datetime] = None
    
    # 🆕 Metadata de Juego
    auto_advance_enabled: bool = True
    manual_control: bool = False  # Permite control manual por admin
    game_speed: str = "normal"  # "slow", "normal", "fast"
    game_end_time: Optional[datetime] = None  # Timestamp cuando termina el juego
    
    # 🆕 Estado de Actividad de Jugadores (Solo para gameplay, no conexiones WebSocket)
    last_game_activity: Dict[str, datetime] = Field(default_factory=dict)  # Última acción en el juego
    inactive_players: List[str] = Field(default_factory=list)  # Jugadores inactivos por tiempo
    
    @classmethod
    def from_game(cls, game: Game) -> "GameExtended":
        """
        Convierte un Game normal a GameExtended con valores por defecto.
        Útil para migración de datos existentes.
        """
        # Mapear GameStatus a GamePhase
        status_to_phase = {
            "waiting": GamePhase.WAITING,
            "started": GamePhase.DAY_DISCUSSION,
            "night": GamePhase.NIGHT_ACTIONS,
            "day": GamePhase.DAY_DISCUSSION,
            "paused": GamePhase.PAUSED,
            "finished": GamePhase.GAME_OVER
        }
        
        current_phase = status_to_phase.get(game.status.value, GamePhase.WAITING)
        
        return cls(
            # Campos originales
            id=game.id,
            name=game.name,
            max_players=game.max_players,
            creator_id=game.creator_id,
            player_ids=game.player_ids,
            players=game.players,
            status=game.status,
            created_at=game.created_at,
            current_round=game.current_round,
            is_first_night=game.is_first_night,
            night_actions=game.night_actions,
            defeated_players=game.defeated_players,
            votes=game.votes,
            # Nuevos campos con valores por defecto
            current_phase=current_phase,
            phase_start_time=datetime.utcnow(),
            phase_auto_advance=True,
            auto_advance_enabled=True,
            manual_control=False,
            game_speed="normal"
        )
    
    def to_game(self) -> Game:
        """
        Convierte GameExtended de vuelta a Game normal.
        Útil para mantener compatibilidad con código existente.
        """
        return Game(
            id=self.id,
            name=self.name,
            max_players=self.max_players,
            creator_id=self.creator_id,
            player_ids=self.player_ids,
            players=self.players,
            status=self.status,
            created_at=self.created_at,
            current_round=self.current_round,
            is_first_night=self.is_first_night,
            night_actions=self.night_actions,
            defeated_players=self.defeated_players,
            votes=self.votes
        )
    
    def schedule_phase_advance(self, duration_seconds: int) -> None:
        """
        Programa el avance automático de fase usando timestamp.
        Reemplazo para asyncio.create_task() de temporizadores.
        """
        self.next_phase_at = datetime.now().replace(microsecond=0) + \
                           timedelta(seconds=duration_seconds)
        self.phase_duration_seconds = duration_seconds
    
    def is_ready_for_phase_advance(self) -> bool:
        """
        Verifica si el juego está listo para avanzar de fase.
        """
        if not self.auto_advance_enabled or self.manual_control:
            return False
        
        if not self.next_phase_at:
            return False
            
        return datetime.now() >= self.next_phase_at
    
    def clear_phase_timer(self) -> None:
        """
        Limpia el timer de fase (equivalente a cancel() de asyncio.Task).
        """
        self.next_phase_at = None
        self.phase_duration_seconds = None
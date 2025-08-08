from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict
from enum import Enum
import datetime
from typing import Optional

class GameRole(str, Enum):
    VILLAGER = "villager"
    SEER = "seer"
    SHERIFF = "sheriff"
    HUNTER = "hunter"
    WITCH = "witch"
    WILD_CHILD = "wild_child"
    CUPID = "cupid"
    WAREWOLF = "warewolf"
    LOVER = "lover"  # Estado especial, no rol principal
    # Puedes añadir más roles especiales aquí

class RoleInfo(BaseModel):
    role: GameRole
    is_alive: bool = True
    is_revealed: bool = False
    
    # Campos para Wild Child (Niño Salvaje)
    model_player_id: Optional[str] = None  # ID del jugador modelo a seguir
    has_transformed: Optional[bool] = None  # Si se ha convertido en Hombre Lobo
    
    # Campos para Witch (Bruja)
    has_healing_potion: Optional[bool] = None  # Si tiene poción de curación disponible
    has_poison_potion: Optional[bool] = None   # Si tiene poción de veneno disponible
    
    # Campos para Sheriff (Alguacil)
    has_double_vote: Optional[bool] = None     # Si su voto cuenta doble
    can_break_ties: Optional[bool] = None      # Si puede desempatar votaciones
    successor_id: Optional[str] = None         # ID del sucesor elegido antes de morir
    
    # Campos para Hunter (Cazador)
    can_revenge_kill: Optional[bool] = None    # Si puede llevarse a alguien al morir
    has_used_revenge: Optional[bool] = None    # Si ya usó su habilidad de venganza
    
    # Campos para Seer (Vidente)
    has_used_vision_tonight: Optional[bool] = None  # Si ya usó visión esta noche
    
    # Campos para Cupid y Lovers (Enamorados)
    is_cupid: Optional[bool] = None            # Si es Cupido
    is_lover: Optional[bool] = None            # Si está enamorado
    lover_partner_id: Optional[str] = None     # ID del compañero enamorado
    
    # Campos generales para habilidades nocturnas
    has_acted_tonight: Optional[bool] = None   # Si ya actuó en esta noche
    target_player_id: Optional[str] = None     # ID del jugador objetivo de la acción nocturna


class GameStatus(str, Enum):
    WAITING = "waiting"      # Esperando jugadores
    STARTED = "started"      # En curso
    NIGHT = "night"          # Fase de noche
    DAY = "day"              # Fase de día
    PAUSED = "paused"        # Pausada
    FINISHED = "finished"    # Finalizada

class GameBase(BaseModel):
    name: str
    max_players: int = Field(..., gt=3, lt=25)

class GameCreate(GameBase):
    creator_id: str

class Game(GameBase):
    id: str
    creator_id: str
    players: List[str] = []  # Solo almacenamos IDs de jugadores en lugar de objetos User completos
    roles: Dict[str, RoleInfo] = {}  # player_id -> RoleInfo
    status: GameStatus = GameStatus.WAITING
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC))
    current_round: int = 0
    is_first_night: bool = True  # Indica si es la primera noche (condiciones especiales)
    night_actions: Dict[str, Dict[str, str]] = {}  # Acciones nocturnas por tipo y jugador
    day_votes: Dict[str, str] = {}  # Votos diurnos: voter_id -> target_id
    # Otros campos: historial, votos, etc.

    model_config = ConfigDict(from_attributes=True)

# Modelo de respuesta que incluye información completa de jugadores para la API
class GameResponse(GameBase):
    id: str
    creator_id: str
    players: List[Dict] = []  # Lista de jugadores con información básica para la API
    roles: Dict[str, RoleInfo] = {}
    status: GameStatus = GameStatus.WAITING
    created_at: datetime.datetime
    current_round: int = 0
    is_first_night: bool = True
    night_actions: Dict[str, Dict[str, str]] = {}
    day_votes: Dict[str, str] = {}

    model_config = ConfigDict(from_attributes=True)


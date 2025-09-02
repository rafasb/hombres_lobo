from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional, Union, Any
from enum import Enum
import datetime

class Roles(str, Enum):
    VILLAGER = "villager"  # Aldeano: rol básico.
    SEER = "seer"           
    SHERIFF = "sheriff"
    HUNTER = "hunter"
    WITCH = "witch"
    WILD_CHILD = "wild_child"
    CUPID = "cupid"
    WAREWOLF = "warewolf"
    # LOVER = "lover"  # Estado especial, no rol principal
    # Puedes añadir más roles especiales aquí

# Simplificado: un único modelo base con todos los campos usados por roles específicos
class PlayerInfo(BaseModel):
    '''Información de roles (incluye campos específicos para evitar subclases).'''
    # Campos comunes a todos los roles
    role: Roles
    player_id: str
    is_alive: bool = True
    lover_partner_id: Optional[str] = ''

    # Campos generales para habilidades nocturnas / tracking
    has_acted_tonight: Optional[bool] = False
    target_player_id: Optional[str] = ''

    # Vidente (Seer) puede apoyarse en los atributos generales

    # Niño salvaje (Wild Child)
    model_player_id: Optional[str] = ''
    has_transformed: Optional[bool] = False

    # Bruja (Witch)
    has_healing_potion: Optional[bool] = True
    has_poison_potion: Optional[bool] = True

    # Alguacil (Sheriff)
    has_double_vote: Optional[bool] = True
    can_break_ties: Optional[bool] = True
    successor_id: Optional[str] = ''

    # Cazador (Hunter)
    can_revenge_kill: Optional[bool] = True

    # Cupido
    has_cupid_action: Optional[bool] = True

    # Permitir campos extra para compatibilidad con datos provenientes del backend o extensiones
    model_config = ConfigDict(from_attributes=True, extra="allow")

    def set_from_dict(self, data: Dict[str, Any]):
        '''Actualiza los campos del PlayerInfo a partir de un dict (útil para cargar desde DB).'''
        # Asegurar que almenos se dispone de role y es válido
        if 'role' not in data or data['role'] not in Roles.__members__.values():
            raise ValueError("El dict debe contener al menos la clave 'role' para PlayerInfo")
        if 'player_id' not in data:
            raise ValueError("El dict debe contener al menos la clave 'player_id' para PlayerInfo")
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        '''Convierte el PlayerInfo a un dict (útil para guardar en DB).'''
        return self.model_dump()


class GameStatus(str, Enum):
    '''waiting --> Esperando a completar los jugadores,
    started --> Partida iniciada, 
    night --> Fase nocturna, 
    day --> Fase de día, 
    paused --> En Pausa, 
    finished --> Partida finalizada'''
    WAITING = "waiting"      # Esperando jugadores
    STARTING = "starting"  # Iniciando (cuenta atrás)
    STARTED = "started"      # En curso
    NIGHT = "night"          # Fase de noche
    DAY = "day"              # Fase de día
    VOTING = "voting"      # Fase de votación
    TRIAL = "trial"        # Fase de juicio
    EXECUTION = "execution"  # Fase de ejecución
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
    player_ids: List[str] = Field(default_factory=list)  # IDs de jugadores (antes de empezar la partida)
    # Ahora mantenemos una lista de PlayerInfo (ordenada), cada entrada agrupa id + info de rol
    players: Dict[str,PlayerInfo] = Field(default_factory=dict)
    # Eliminado el roles: Dict[...] en favor de players
    status: GameStatus = GameStatus.WAITING
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    current_round: int = 0
    is_first_night: bool = True  # Indica si es la primera noche (condiciones especiales)
    night_actions: Dict[str, Dict[str, str]] = Field(default_factory=dict)  # Acciones nocturnas por tipo y jugador
    day_votes: Dict[str, str] = Field(default_factory=dict)  # Votos diurnos: voter_id -> target_id
    # Otros campos: historial, votos, etc.

    model_config = ConfigDict(from_attributes=True)

    # Helpers mínimos (puedes extenderlos donde instancies Game)
    def get_player_state(self, player_id: str) -> Optional[PlayerInfo]:
        """
        Devuelve el PlayerInfo asociado a un player_id específico.
        
        Args:
            player_id: ID del jugador específico
            
        Returns:
            PlayerInfo si existe, None en caso contrario
        """
        return self.players.get(player_id)
    
    
    @property
    def player_states(self) -> List[PlayerInfo]:
        """
        Devuelve una lista con todos los PlayerInfos de la partida.
        
        Returns:
            Lista de todos los PlayerInfos en el juego
        """
        return list(self.players.values())
    
    def to_dict(self) -> Dict[str, Any]:
        '''Convierte el Game a un dict (útil para guardar en DB).'''
        data = self.model_dump()
        # Convertir players a dicts
        data['players'] = {pid: p.to_dict() for pid, p in self.players.items()}
        return data

    def set_player_info(self, player_id: str, info: Union[PlayerInfo, Dict[str, Any]]):
        """
        Establece o añade la información de rol de un jugador en self.players (Dict[str, PlayerInfo]).
        Si ya existe, fusiona los datos previos con los nuevos (los campos de `info` prevalecen).
        Acepta tanto instancias de PlayerInfoBase/PlayerInfo como dicts.
        """
        # Normalizar info a dict
        
        if isinstance(info, dict):
            info_data = info.copy()
        elif isinstance(info, PlayerInfo):
            info_data = info.model_dump()
        else:
           raise TypeError("info must be a dict or a Pydantic model (PlayerInfo/PlayerInfo)")

        # Forzar player_id en el estado resultante
        info_data['player_id'] = player_id

        # Si existe un estado previo, fusionarlo con los nuevos datos (los nuevos prevalecen)
        existing = self.get_player_state(player_id)
        if existing and isinstance(existing, PlayerInfo):
            merged = {**existing.model_dump(), **info_data}
            merged['player_id'] = player_id
            self.players[player_id] = PlayerInfo(**merged)
        else:
            self.players[player_id] = PlayerInfo(**info_data)


from pydantic import BaseModel, Field
from typing import List, Dict
from .user import User
from .roles import RoleInfo
from enum import Enum
import datetime

class GameStatus(str, Enum):
    WAITING = "waiting"      # Esperando jugadores
    STARTED = "started"      # En curso
    NIGHT = "night"          # Fase de noche
    DAY = "day"              # Fase de día
    FINISHED = "finished"    # Finalizada

class GameBase(BaseModel):
    name: str
    max_players: int = Field(..., gt=3, lt=25)

class GameCreate(GameBase):
    creator_id: str

class Game(GameBase):
    id: str
    creator_id: str
    players: List[User] = []
    roles: Dict[str, RoleInfo] = {}  # player_id -> RoleInfo
    status: GameStatus = GameStatus.WAITING
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    current_round: int = 0
    # Otros campos: historial, votos, etc.

    class Config:
        orm_mode = True

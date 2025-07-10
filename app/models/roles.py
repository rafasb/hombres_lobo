from enum import Enum
from pydantic import BaseModel
from typing import Optional

class GameRole(str, Enum):
    VILLAGER = "villager"
    SEER = "seer"
    SHERIFF = "sheriff"
    HUNTER = "hunter"
    WITCH = "witch"
    WILD_CHILD = "wild_child"
    CUPID = "cupid"
    WEREWOLF = "werewolf"
    LOVER = "lover"  # Estado especial, no rol principal
    # Puedes añadir más roles especiales aquí

class RoleInfo(BaseModel):
    role: GameRole
    is_alive: bool = True
    is_revealed: bool = False
    # Campos opcionales para habilidades o estados especiales
    model_player_id: Optional[str] = None  # Para wild_child
    has_healing_potion: Optional[bool] = None  # Para witch
    has_poison_potion: Optional[bool] = None  # Para witch
    is_cupid: Optional[bool] = None
    is_lover: Optional[bool] = None
    # Puedes añadir más campos según la lógica del juego

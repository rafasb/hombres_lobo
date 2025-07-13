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

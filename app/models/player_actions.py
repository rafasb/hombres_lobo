"""
Modelos de datos para las acciones de los jugadores durante las partidas.
Define las estructuras de datos para requests y responses de las acciones específicas de cada rol.
"""

from pydantic import BaseModel
from typing import Optional, List, Dict


class WarewolfAttackRequest(BaseModel):
    """Modelo para el request de ataque de hombre lobo."""
    target_id: str


class DayVoteRequest(BaseModel):
    """Modelo para el request de votación diurna."""
    target_id: str


class PlayerInfo(BaseModel):
    """Información básica de un jugador."""
    id: str
    username: str


class VoteCount(BaseModel):
    """Información de recuento de votos."""
    player_id: str
    username: str
    vote_count: int


class WarewolfAttackResponse(BaseModel):
    """Respuesta del endpoint de ataque de hombre lobo."""
    success: bool
    message: str
    consensus_target: Optional[str] = None


class DayVoteResponse(BaseModel):
    """Respuesta del endpoint de votación diurna."""
    success: bool
    message: str
    vote_counts: List[VoteCount] = []
    total_votes: int = 0
    total_players: int = 0


class SeerVisionRequest(BaseModel):
    """Modelo para el request de visión de la vidente."""
    target_id: str


class SeerVisionResponse(BaseModel):
    """Respuesta del endpoint de visión de la vidente."""
    success: bool
    message: str
    target_role: Optional[str] = None
    target_username: Optional[str] = None


class SheriffTiebreakerRequest(BaseModel):
    """Modelo para el request de desempate del alguacil."""
    target_id: str


class SheriffSuccessorRequest(BaseModel):
    """Modelo para el request de elección de sucesor del alguacil."""
    successor_id: str


class SheriffTiebreakerResponse(BaseModel):
    """Respuesta del endpoint de desempate del alguacil."""
    success: bool
    message: str
    eliminated_player_id: str
    eliminated_username: str


class SheriffSuccessorResponse(BaseModel):
    """Respuesta del endpoint de elección de sucesor del alguacil."""
    success: bool
    message: str
    successor_id: str
    successor_username: str


class HunterRevengeRequest(BaseModel):
    """Modelo para el request de venganza del cazador."""
    target_id: str


class HunterRevengeResponse(BaseModel):
    """Respuesta del endpoint de venganza del cazador."""
    success: bool
    message: str
    target_id: str
    target_username: str


class WitchHealRequest(BaseModel):
    """Modelo para el request de curación de la bruja."""
    target_id: str  # ID del jugador a curar (víctima del ataque de lobos)


class WitchPoisonRequest(BaseModel):
    """Modelo para el request de envenenamiento de la bruja."""
    target_id: str  # ID del jugador a envenenar


class WitchHealResponse(BaseModel):
    """Respuesta del endpoint de curación de la bruja."""
    success: bool
    message: str
    healed_player_id: str
    healed_username: str


class WitchPoisonResponse(BaseModel):
    """Respuesta del endpoint de envenenamiento de la bruja."""
    success: bool
    message: str
    poisoned_player_id: str
    poisoned_username: str


class WitchNightInfoResponse(BaseModel):
    """Respuesta con información de la noche para la bruja."""
    success: bool
    message: str
    attacked_player_id: Optional[str] = None
    attacked_username: Optional[str] = None
    can_heal: bool = False
    can_poison: bool = False


# Modelos para El Niño Salvaje

class WildChildChooseModelRequest(BaseModel):
    """Modelo para elegir el jugador modelo del Niño Salvaje."""
    model_player_id: str  # ID del jugador modelo a seguir


class WildChildChooseModelResponse(BaseModel):
    """Respuesta del endpoint de elección de modelo."""
    success: bool
    message: str
    model_player_id: str
    model_username: str


class WildChildStatusResponse(BaseModel):
    """Respuesta con el estado actual del Niño Salvaje."""
    success: bool
    message: str
    has_model: bool = False
    model_player_id: Optional[str] = None
    model_username: Optional[str] = None
    is_transformed: bool = False
    current_role: str  # "wild_child" o "warewolf"


class WildChildTransformationResponse(BaseModel):
    """Respuesta cuando el Niño Salvaje se transforma."""
    success: bool
    message: str
    transformed: bool
    new_role: str
    reason: str  # Motivo de la transformación


class WildChildAvailableModelsResponse(BaseModel):
    """Respuesta con jugadores disponibles como modelo."""
    success: bool
    message: str
    available_models: List[Dict[str, str]]  # Lista de {id, username}


# Modelos para Cupido (Cupid)
class CupidChooseLoversRequest(BaseModel):
    """Solicitud para que Cupido elija a los enamorados."""
    lover1_id: str
    lover2_id: str


class CupidChooseLoversResponse(BaseModel):
    """Respuesta cuando Cupido elige a los enamorados."""
    success: bool
    message: str
    lover1_id: str
    lover1_username: str
    lover2_id: str
    lover2_username: str


class CupidStatusResponse(BaseModel):
    """Respuesta con el estado actual de Cupido."""
    success: bool
    message: str
    has_chosen_lovers: bool = False
    lover1_id: Optional[str] = None
    lover1_username: Optional[str] = None
    lover2_id: Optional[str] = None
    lover2_username: Optional[str] = None


class CupidAvailableTargetsResponse(BaseModel):
    """Respuesta con jugadores disponibles para enamorar."""
    success: bool
    message: str
    available_targets: List[Dict[str, str]]  # Lista de {id, username}


class LoversStatusResponse(BaseModel):
    """Respuesta con el estado de los enamorados."""
    success: bool
    message: str
    is_lover: bool = False
    partner_id: Optional[str] = None
    partner_username: Optional[str] = None
    both_alive: bool = False

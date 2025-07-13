"""
Modelos de datos para las acciones de los jugadores durante las partidas.
Define las estructuras de datos para requests y responses de las acciones específicas de cada rol.
"""

from pydantic import BaseModel
from typing import Optional


class WerewolfAttackRequest(BaseModel):
    """Modelo para el request de ataque de hombre lobo."""
    target_id: str


class PlayerInfo(BaseModel):
    """Información básica de un jugador."""
    id: str
    username: str


class WerewolfAttackResponse(BaseModel):
    """Respuesta del endpoint de ataque de hombre lobo."""
    success: bool
    message: str
    consensus_target: Optional[str] = None

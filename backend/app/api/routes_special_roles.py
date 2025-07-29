"""
Rutas de API para las acciones de roles especiales durante las partidas.
Incluye endpoints específicos para roles como Vidente, Bruja, Cazador, etc.
Requiere autenticación JWT para acceder.
"""

from fastapi import APIRouter, HTTPException, Depends
from app.models.player_actions import (
    SeerVisionRequest,
    SeerVisionResponse,
    PlayerInfo,
)
from app.services.player_action_service import (
    can_seer_act,
    seer_vision,
    get_seer_vision_result,
    get_seer_eligible_targets,
)
from app.core.dependencies import get_current_user
from typing import List, Dict

router = APIRouter()


@router.post("/games/{game_id}/seer-vision", response_model=SeerVisionResponse)
def use_seer_vision(
    game_id: str,
    vision_request: SeerVisionRequest,
    user=Depends(get_current_user)
):
    """
    Permite a la vidente investigar el rol de otro jugador durante la fase nocturna.
    
    Args:
        game_id: ID de la partida
        vision_request: Contiene el ID del jugador a investigar
        user: Usuario actual (debe ser la vidente)
    
    Returns:
        Respuesta con el resultado de la investigación
    """
    # Verificar si el jugador puede actuar como vidente
    if not can_seer_act(game_id, user.id):
        raise HTTPException(
            status_code=400,
            detail="No puedes usar tu habilidad de vidente en este momento"
        )
    
    # Realizar la visión
    updated_game = seer_vision(game_id, user.id, vision_request.target_id)
    if not updated_game:
        raise HTTPException(
            status_code=400,
            detail="No se pudo realizar la investigación. Verifica que el objetivo sea válido."
        )
    
    # Obtener el resultado de la visión
    vision_result = get_seer_vision_result(game_id, user.id, vision_request.target_id)
    if not vision_result:
        raise HTTPException(
            status_code=400,
            detail="No se pudo obtener el resultado de la investigación"
        )
    
    response = SeerVisionResponse(
        success=True,
        message=f"Has investigado a {vision_result['username']}",
        target_role=vision_result["role"],
        target_username=vision_result["username"]
    )
    
    return response


@router.get("/games/{game_id}/seer-targets", response_model=List[PlayerInfo])
def get_seer_targets(game_id: str, user=Depends(get_current_user)):
    """
    Obtiene la lista de jugadores que la vidente puede investigar.
    
    Args:
        game_id: ID de la partida
        user: Usuario actual (debe ser la vidente)
    
    Returns:
        Lista de jugadores vivos que pueden ser investigados
    """
    # Verificar si el jugador puede actuar como vidente
    if not can_seer_act(game_id, user.id):
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para ver esta información"
        )
    
    eligible_targets = get_seer_eligible_targets(game_id, user.id)
    return [PlayerInfo(**target) for target in eligible_targets]


@router.get("/games/{game_id}/can-seer-act", response_model=Dict[str, bool])
def check_seer_can_act(game_id: str, user=Depends(get_current_user)):
    """
    Verifica si el usuario puede usar su habilidad de vidente.
    
    Args:
        game_id: ID de la partida
        user: Usuario actual
    
    Returns:
        Diccionario indicando si puede usar su habilidad de vidente
    """
    can_act = can_seer_act(game_id, user.id)
    return {"can_act": can_act}

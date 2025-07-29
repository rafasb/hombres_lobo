"""
Rutas de API para las acciones del Cazador durante las partidas.
Incluye endpoints específicos para la habilidad de venganza cuando es eliminado.
Requiere autenticación JWT para acceder.
"""

from fastapi import APIRouter, HTTPException, Depends
from app.models.player_actions import (
    HunterRevengeRequest,
    HunterRevengeResponse,
    PlayerInfo,
)
from app.services.player_action_service import (
    is_hunter,
    can_hunter_revenge,
    hunter_revenge_kill,
    get_hunter_revenge_targets,
    check_hunter_death_triggers,
    auto_eliminate_hunter_target,
)
from app.core.dependencies import get_current_user
from typing import List, Dict

router = APIRouter()


@router.post("/games/{game_id}/hunter-revenge", response_model=HunterRevengeResponse)
def execute_hunter_revenge(
    game_id: str,
    revenge_request: HunterRevengeRequest,
    user=Depends(get_current_user)
):
    """
    Permite al cazador llevarse a otro jugador cuando es eliminado.
    
    Args:
        game_id: ID de la partida
        revenge_request: Contiene el ID del jugador objetivo para la venganza
        user: Usuario actual (debe ser el cazador eliminado)
    
    Returns:
        Respuesta con el resultado de la venganza
    """
    # Verificar si el jugador puede usar venganza
    if not can_hunter_revenge(game_id, user.id):
        raise HTTPException(
            status_code=400,
            detail="No puedes usar tu habilidad de venganza en este momento"
        )
    
    # Ejecutar la venganza
    updated_game = hunter_revenge_kill(game_id, user.id, revenge_request.target_id)
    if not updated_game:
        raise HTTPException(
            status_code=400,
            detail="No se pudo ejecutar la venganza. Verifica que el objetivo sea válido."
        )
    
    # Buscar información del objetivo eliminado
    target_username = None
    for player in updated_game.players:
        if player.id == revenge_request.target_id:
            target_username = player.username
            break
    
    if not target_username:
        raise HTTPException(
            status_code=400,
            detail="No se pudo encontrar información del objetivo"
        )
    
    response = HunterRevengeResponse(
        success=True,
        message=f"Te has llevado a {target_username} contigo en tu venganza final.",
        target_id=revenge_request.target_id,
        target_username=target_username
    )
    
    return response


@router.get("/games/{game_id}/hunter-revenge-targets", response_model=List[PlayerInfo])
def get_revenge_targets(game_id: str, user=Depends(get_current_user)):
    """
    Obtiene la lista de jugadores que el cazador puede eliminar por venganza.
    
    Args:
        game_id: ID de la partida
        user: Usuario actual (debe ser el cazador eliminado)
    
    Returns:
        Lista de jugadores vivos que pueden ser objetivo de venganza
    """
    # Verificar si el jugador puede usar venganza
    if not can_hunter_revenge(game_id, user.id):
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para ver esta información"
        )
    
    eligible_targets = get_hunter_revenge_targets(game_id, user.id)
    return [PlayerInfo(**target) for target in eligible_targets]


@router.get("/games/{game_id}/can-hunter-revenge", response_model=Dict[str, bool])
def check_can_revenge(game_id: str, user=Depends(get_current_user)):
    """
    Verifica si el cazador puede usar su habilidad de venganza.
    
    Args:
        game_id: ID de la partida
        user: Usuario actual
    
    Returns:
        Diccionario indicando si puede usar venganza
    """
    can_revenge = can_hunter_revenge(game_id, user.id)
    return {"can_revenge": can_revenge}


@router.get("/games/{game_id}/is-hunter", response_model=Dict[str, bool])
def check_is_hunter(game_id: str, user=Depends(get_current_user)):
    """
    Verifica si el usuario es el cazador de la partida.
    
    Args:
        game_id: ID de la partida
        user: Usuario actual
    
    Returns:
        Diccionario indicando si es el cazador
    """
    hunter_status = is_hunter(game_id, user.id)
    return {"is_hunter": hunter_status}


@router.get("/games/{game_id}/hunters-needing-revenge", response_model=List[str])
def get_hunters_needing_revenge(game_id: str, user=Depends(get_current_user)):
    """
    Obtiene la lista de cazadores que murieron y necesitan activar su venganza.
    Solo accesible por administradores o el narrador del juego.
    
    Args:
        game_id: ID de la partida
        user: Usuario actual (debe tener permisos administrativos)
    
    Returns:
        Lista de IDs de cazadores que pueden vengarse
    """
    # Verificar permisos - por ahora solo verificamos que esté en la partida
    from app.services.game_service import get_game
    game = get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Partida no encontrada")
    
    # Verificar que el usuario está en la partida o es admin
    user_in_game = any(player.id == user.id for player in game.players)
    if not user_in_game:
        raise HTTPException(
            status_code=403,
            detail="No estás participando en esta partida"
        )
    
    hunters_needing_revenge = check_hunter_death_triggers(game_id)
    return hunters_needing_revenge


@router.get("/games/{game_id}/hunter-revenge-result/{hunter_id}", response_model=Dict[str, str])
def get_hunter_revenge_result(
    game_id: str, 
    hunter_id: str, 
    user=Depends(get_current_user)
):
    """
    Obtiene el resultado de la venganza de un cazador específico.
    
    Args:
        game_id: ID de la partida
        hunter_id: ID del cazador
        user: Usuario actual
    
    Returns:
        Información del objetivo eliminado por venganza
    """
    # Verificar que el usuario está en la partida
    from app.services.game_service import get_game
    game = get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Partida no encontrada")
    
    user_in_game = any(player.id == user.id for player in game.players)
    if not user_in_game:
        raise HTTPException(
            status_code=403,
            detail="No estás participando en esta partida"
        )
    
    revenge_result = auto_eliminate_hunter_target(game_id, hunter_id)
    if not revenge_result:
        raise HTTPException(
            status_code=404,
            detail="No se encontró resultado de venganza para este cazador"
        )
    
    return revenge_result


@router.get("/games/{game_id}/my-hunter-status", response_model=Dict[str, bool])
def get_my_hunter_status(game_id: str, user=Depends(get_current_user)):
    """
    Obtiene el estado completo del cazador para el usuario actual.
    
    Args:
        game_id: ID de la partida
        user: Usuario actual
    
    Returns:
        Estado completo del cazador (si es cazador, si puede vengarse, etc.)
    """
    # Verificar que es cazador
    hunter_status = is_hunter(game_id, user.id)
    can_revenge = can_hunter_revenge(game_id, user.id) if hunter_status else False
    
    # Obtener estado adicional del cazador
    from app.services.game_service import get_game
    game = get_game(game_id)
    is_alive = False
    has_used_revenge = False
    
    if game and user.id in game.roles:
        role_info = game.roles[user.id]
        if role_info.role.value == "hunter":
            is_alive = role_info.is_alive
            has_used_revenge = role_info.has_used_revenge or False
    
    return {
        "is_hunter": hunter_status,
        "can_revenge": can_revenge,
        "is_alive": is_alive,
        "has_used_revenge": has_used_revenge
    }

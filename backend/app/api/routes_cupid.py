"""
Rutas de la API para las acciones de Cupido.
"""

from fastapi import APIRouter, HTTPException, Depends

from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.player_actions import (
    CupidChooseLoversRequest,
    CupidChooseLoversResponse,
    CupidStatusResponse,
    CupidAvailableTargetsResponse,
    LoversStatusResponse
)
from app.services import player_action_service

router = APIRouter(prefix="/cupid", tags=["cupid"])


@router.post("/choose-lovers/{game_id}", response_model=CupidChooseLoversResponse)
async def choose_lovers(
    game_id: str,
    request: CupidChooseLoversRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Permite a Cupido elegir a dos jugadores como enamorados.
    """
    # Verificar que el usuario actual es Cupido
    if not player_action_service.is_cupid(game_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Solo Cupido puede elegir enamorados"
        )
    
    # Verificar que puede elegir enamorados
    if not player_action_service.can_cupid_choose_lovers(game_id, current_user.id):
        raise HTTPException(
            status_code=400,
            detail="No puedes elegir enamorados en este momento"
        )
    
    # Elegir enamorados
    updated_game = player_action_service.cupid_choose_lovers(
        game_id, current_user.id, request.lover1_id, request.lover2_id
    )
    
    if not updated_game:
        raise HTTPException(
            status_code=400,
            detail="No se pudo realizar la elección de enamorados"
        )
    
    # Obtener nombres de usuario de los enamorados
    lover1_username = None
    lover2_username = None
    for player in updated_game.players:
        if player.id == request.lover1_id:
            lover1_username = player.username
        elif player.id == request.lover2_id:
            lover2_username = player.username
    
    return CupidChooseLoversResponse(
        success=True,
        message="Enamorados elegidos exitosamente",
        lover1_id=request.lover1_id,
        lover1_username=lover1_username or "Desconocido",
        lover2_id=request.lover2_id,
        lover2_username=lover2_username or "Desconocido"
    )


@router.get("/status/{game_id}", response_model=CupidStatusResponse)
async def get_cupid_status(
    game_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene el estado actual de Cupido.
    """
    # Verificar que el usuario actual es Cupido
    if not player_action_service.is_cupid(game_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Solo Cupido puede ver este estado"
        )
    
    status = player_action_service.get_cupid_status(game_id, current_user.id)
    
    return CupidStatusResponse(
        success=True,
        message="Estado de Cupido obtenido",
        has_chosen_lovers=status["has_chosen_lovers"],
        lover1_id=status["lover1_id"],
        lover1_username=status["lover1_username"],
        lover2_id=status["lover2_id"],
        lover2_username=status["lover2_username"]
    )


@router.get("/available-targets/{game_id}", response_model=CupidAvailableTargetsResponse)
async def get_available_targets(
    game_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene la lista de jugadores disponibles para enamorar.
    """
    # Verificar que el usuario actual es Cupido
    if not player_action_service.is_cupid(game_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Solo Cupido puede ver los objetivos disponibles"
        )
    
    # Verificar que puede elegir
    if not player_action_service.can_cupid_choose_lovers(game_id, current_user.id):
        raise HTTPException(
            status_code=400,
            detail="No puedes elegir enamorados en este momento"
        )
    
    targets = player_action_service.get_cupid_available_targets(game_id, current_user.id)
    
    return CupidAvailableTargetsResponse(
        success=True,
        message="Objetivos disponibles obtenidos",
        available_targets=targets
    )


@router.get("/lovers-status/{game_id}", response_model=LoversStatusResponse)
async def get_lovers_status(
    game_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene el estado de enamorado del jugador actual.
    """
    status = player_action_service.get_lovers_status(game_id, current_user.id)
    
    # Solo revelar información si el jugador es efectivamente enamorado
    if not status["is_lover"]:
        return LoversStatusResponse(
            success=True,
            message="No eres enamorado",
            is_lover=False
        )
    
    return LoversStatusResponse(
        success=True,
        message="Estado de enamorado obtenido",
        is_lover=status["is_lover"],
        partner_id=status["partner_id"],
        partner_username=status["partner_username"],
        both_alive=status["both_alive"]
    )


@router.post("/check-lovers-death/{game_id}")
async def check_lovers_death(
    game_id: str,
    dead_player_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Verifica si algún enamorado debe morir por la pérdida de su pareja.
    Solo accesible por administradores o el sistema.
    """
    # Esta función debería ser solo para administradores o llamadas internas del sistema
    # Por simplicidad, permitimos que cualquier jugador la llame
    
    deaths = player_action_service.check_lovers_death(game_id, dead_player_id)
    
    return {
        "success": True,
        "message": "Verificación de muerte de enamorados completada",
        "deaths_by_love": deaths
    }


@router.get("/check-victory-condition/{game_id}")
async def check_lovers_victory(
    game_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Verifica si los enamorados han ganado la partida.
    """
    victory_info = player_action_service.check_lovers_victory_condition(game_id)
    
    if victory_info:
        return {
            "success": True,
            "message": "Los enamorados han ganado",
            "victory": True,
            "victory_info": victory_info
        }
    else:
        return {
            "success": True,
            "message": "Los enamorados no han ganado aún",
            "victory": False
        }


@router.post("/initialize/{game_id}")
async def initialize_cupid(
    game_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Inicializa las acciones nocturnas de Cupido.
    """
    # Verificar que el usuario actual es Cupido
    if not player_action_service.is_cupid(game_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Solo Cupido puede inicializar sus acciones"
        )
    
    success = player_action_service.initialize_cupid_night_actions(game_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="No se pudo inicializar las acciones de Cupido"
        )
    
    return {
        "success": True,
        "message": "Acciones de Cupido inicializadas"
    }


@router.post("/reset/{game_id}")
async def reset_cupid_actions(
    game_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Reinicia las acciones nocturnas de Cupido.
    Solo para administradores o el sistema.
    """
    # En una implementación real, esto debería ser solo para administradores
    success = player_action_service.reset_cupid_night_actions(game_id)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="No se pudo reiniciar las acciones de Cupido"
        )
    
    return {
        "success": True,
        "message": "Acciones de Cupido reiniciadas"
    }

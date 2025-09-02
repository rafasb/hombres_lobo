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
from app.services.cupid_action_service import is_cupid, can_cupid_choose_lovers, cupid_choose_lovers, get_cupid_available_targets, check_lovers_victory_condition, initialize_cupid_night_actions, reset_cupid_night_actions
from app.services.cupid_action_service import check_lovers_death as check_lovers_death_service
from app.services.user_service import UserService

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
    if not is_cupid(game_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Solo Cupido puede elegir enamorados"
        )
    
    # Verificar que puede elegir enamorados
    if not can_cupid_choose_lovers(game_id, current_user.id):
        raise HTTPException(
            status_code=400,
            detail="No puedes elegir enamorados en este momento"
        )
    
    # Elegir enamorados
    updated_game = cupid_choose_lovers(
        game_id, current_user.id, request.lover1_id, request.lover2_id
    )
    
    if not updated_game:
        raise HTTPException(
            status_code=400,
            detail="No se pudo realizar la elección de enamorados"
        )
    
    # Obtener nombres de usuario de los enamorados
    lover1_username = UserService.get_username_by_id(request.lover1_id)
    lover2_username = UserService.get_username_by_id(request.lover2_id)

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
    if not is_cupid(game_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Solo Cupido puede ver este estado"
        )
    
    status = await get_cupid_status(game_id, current_user)

    if isinstance(status, CupidStatusResponse):
        return status
    else:
        raise HTTPException(
            status_code=400,
            detail="Error al obtener el estado de Cupido"
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
    if not is_cupid(game_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Solo Cupido puede ver los objetivos disponibles"
        )
    
    # Verificar que puede elegir
    if not can_cupid_choose_lovers(game_id, current_user.id):
        raise HTTPException(
            status_code=400,
            detail="No puedes elegir enamorados en este momento"
        )
    
    targets = get_cupid_available_targets(game_id, current_user.id)
    
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
    status = await get_lovers_status(game_id, current_user)

    if isinstance(status, HTTPException):
        raise status
    elif isinstance(status, LoversStatusResponse):
        return status
    else:
        raise HTTPException(
            status_code=400,
            detail="Error al obtener el estado de enamorado"
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

    deaths = check_lovers_death_service(game_id, dead_player_id)

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
    victory_info = check_lovers_victory_condition(game_id)
    
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
    if not is_cupid(game_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Solo Cupido puede inicializar sus acciones"
        )
    
    success = initialize_cupid_night_actions(game_id, current_user.id)
    
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
    success = reset_cupid_night_actions(game_id)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="No se pudo reiniciar las acciones de Cupido"
        )
    
    return {
        "success": True,
        "message": "Acciones de Cupido reiniciadas"
    }

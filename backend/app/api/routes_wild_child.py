# routes_wild_child.py
# Endpoints específicos para las acciones del Niño Salvaje

from fastapi import APIRouter, HTTPException, Depends
from app.core.dependencies import get_current_user
from app.services.wild_child_action_service import (
    is_wild_child, can_wild_child_choose_model,
    get_available_models_for_wild_child, wild_child_choose_model, 
    check_wild_child_transformation, notify_werewolves_of_new_member, 
    get_wild_child_transformation_info, process_wild_child_death_check
)
from app.models.player_actions import (
    WildChildChooseModelRequest, WildChildChooseModelResponse,
    WildChildStatusResponse, WildChildAvailableModelsResponse
)
from app.services import game_service
from app.services.user_service import UserService

router = APIRouter(prefix="/wild-child", tags=["wild-child"])


@router.get("/status/{game_id}", response_model=WildChildStatusResponse)
async def get_wild_child_status(
    game_id: str,
    current_user = Depends(get_current_user)
):
    """
    Obtiene el estado actual del Niño Salvaje: si tiene modelo, si se transformó, etc.
    """
    wild_child_id = current_user.id
    
    # Verificar que el jugador es el Niño Salvaje
    if not is_wild_child(game_id, wild_child_id):
        raise HTTPException(
            status_code=403,
            detail="Solo el Niño Salvaje puede acceder a esta información"
        )
    
    status_info: WildChildStatusResponse = await get_wild_child_status(game_id, wild_child_id)
    
    if not status_info:
        raise HTTPException(
            status_code=404,
            detail="No se pudo obtener información del Niño Salvaje"
        )
    
    has_model = status_info.has_model if hasattr(status_info, 'has_model') else False
    model_player_id = status_info.model_player_id if hasattr(status_info, 'model_player_id') else None
    model_username = status_info.model_username if hasattr(status_info, 'model_username') else None

    return WildChildStatusResponse(
        success=True,
        message="Estado del Niño Salvaje obtenido correctamente",
        has_model=has_model,
        model_player_id=model_player_id,
        model_username=model_username,
        is_transformed=status_info.is_transformed if hasattr(status_info, 'is_transformed') else False,
        current_role=status_info.current_role if hasattr(status_info, 'current_role') else "wild_child"
    )


@router.get("/available-models/{game_id}", response_model=WildChildAvailableModelsResponse)
async def get_available_models(
    game_id: str,
    current_user = Depends(get_current_user)
):
    """
    Obtiene la lista de jugadores que pueden ser elegidos como modelo.
    """
    wild_child_id = current_user.id
    
    # Verificar que el jugador es el Niño Salvaje
    if not is_wild_child(game_id, wild_child_id):
        raise HTTPException(
            status_code=403,
            detail="Solo el Niño Salvaje puede acceder a esta información"
        )
    
    available_models = get_available_models_for_wild_child(game_id, wild_child_id)
    
    return WildChildAvailableModelsResponse(
        success=True,
        message=f"Se encontraron {len(available_models)} modelos disponibles",
        available_models=available_models
    )


@router.post("/choose-model", response_model=WildChildChooseModelResponse)
async def choose_model(
    game_id: str,
    request: WildChildChooseModelRequest,
    current_user = Depends(get_current_user)
):
    """
    Permite al Niño Salvaje elegir su jugador modelo en la primera noche.
    """
    wild_child_id = current_user.id
    
    # Verificar que el jugador es el Niño Salvaje y puede elegir modelo
    if not can_wild_child_choose_model(game_id, wild_child_id):
        raise HTTPException(
            status_code=403,
            detail="No puedes elegir un modelo en este momento"
        )
    
    # Obtener información del modelo elegido
    game = game_service.get_game(game_id)
    model_username = None
    if game:
        for player in game.players:
            if player == request.model_player_id:
                model_username = UserService.get_username_by_id(player)
                break
    
    if not model_username:
        raise HTTPException(
            status_code=400,
            detail="El jugador elegido como modelo no existe"
        )
    
    # Realizar la elección
    updated_game = wild_child_choose_model(
        game_id, wild_child_id, request.model_player_id
    )
    
    if not updated_game:
        raise HTTPException(
            status_code=400,
            detail="No se pudo elegir el modelo"
        )
    
    return WildChildChooseModelResponse(
        success=True,
        message=f"Has elegido a {model_username} como tu modelo a seguir",
        model_player_id=request.model_player_id,
        model_username=model_username
    )


@router.get("/can-choose-model/{game_id}")
async def check_can_choose_model(
    game_id: str,
    current_user = Depends(get_current_user)
):
    """
    Verifica si el Niño Salvaje puede elegir un modelo en este momento.
    """
    wild_child_id = current_user.id
    
    can_choose = can_wild_child_choose_model(game_id, wild_child_id)
    
    return {
        "success": True,
        "can_choose_model": can_choose,
        "message": "Puedes elegir un modelo" if can_choose else "No puedes elegir un modelo en este momento"
    }


@router.get("/transformation-info/{game_id}")
async def get_transformation_info(
    game_id: str,
    current_user = Depends(get_current_user)
):
    """
    Obtiene información detallada sobre la transformación del Niño Salvaje.
    """
    wild_child_id = current_user.id
    
    # Verificar que el jugador es o era el Niño Salvaje
    transformation_info = get_wild_child_transformation_info(game_id, wild_child_id)
    
    if not transformation_info:
        raise HTTPException(
            status_code=404,
            detail="No se encontró información de transformación"
        )
    
    return {
        "success": True,
        "transformation_info": transformation_info,
        "message": "Información de transformación obtenida correctamente"
    }


@router.post("/check-transformation/{game_id}")
async def check_transformation_trigger(
    game_id: str,
    dead_player_id: str,
    current_user = Depends(get_current_user)
):
    """
    Verifica si la muerte de un jugador específico causa la transformación del Niño Salvaje.
    (Endpoint para uso administrativo o del sistema)
    """
    # Este endpoint podría ser usado por el sistema para verificar transformaciones
    # después de muertes en el juego
    
    transformations = check_wild_child_transformation(game_id, dead_player_id)
    
    return {
        "success": True,
        "transformations": transformations,
        "message": f"Se procesaron {len(transformations)} transformaciones"
    }


@router.get("/werewolf-notification/{game_id}")
async def get_werewolf_notification(
    game_id: str,
    current_user = Depends(get_current_user)
):
    """
    Obtiene información sobre nuevos miembros de la manada para hombres lobo existentes.
    """
    user_id = current_user.id
    
    # Verificar que el usuario es un hombre lobo
    game = game_service.get_game(game_id)
    if not game or user_id not in game.players:
        raise HTTPException(
            status_code=404,
            detail="Partida o jugador no encontrado"
        )
    
    user_role = game.players[user_id]
    if user_role.role != "warewolf" or not user_role.is_alive:
        raise HTTPException(
            status_code=403,
            detail="Solo los hombres lobo pueden acceder a esta información"
        )
    
    # Buscar Niños Salvajes transformados recientemente
    new_werewolves = []
    for player_id, role_info in game.players.items():
        if (role_info.role == "warewolf" and 
            role_info.has_transformed and
            player_id != user_id):
            
            # Obtener nombre del jugador
            for player in game.players:
                if player == player_id:
                    new_werewolves.append({
                        "id": player_id,
                        "username": UserService.get_username_by_id(player),
                        "original_role": "wild_child"
                    })
                    break
    
    return {
        "success": True,
        "new_werewolves": new_werewolves,
        "message": f"Se encontraron {len(new_werewolves)} nuevos miembros de la manada"
    }


@router.post("/initialize/{game_id}")
async def initialize_wild_child(
    game_id: str,
    current_user = Depends(get_current_user)
):
    """
    Inicializa al Niño Salvaje al comienzo del juego.
    """
    wild_child_id = current_user.id
    
    success = initialize_wild_child(game_id, wild_child_id)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="No se pudo inicializar al Niño Salvaje"
        )
    
    return {
        "success": True,
        "message": "Niño Salvaje inicializado correctamente"
    }


@router.post("/process-death-checks/{game_id}")
async def process_death_checks(
    game_id: str,
    current_user = Depends(get_current_user)
):
    """
    Procesa todas las verificaciones de muerte para posibles transformaciones.
    (Endpoint para uso del sistema después de procesar muertes)
    """
    transformations = process_wild_child_death_check(game_id)
    
    return {
        "success": True,
        "transformations": transformations,
        "message": f"Se procesaron {len(transformations)} verificaciones de transformación"
    }

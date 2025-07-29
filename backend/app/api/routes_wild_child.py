# routes_wild_child.py
# Endpoints específicos para las acciones del Niño Salvaje

from fastapi import APIRouter, HTTPException, Depends
from app.core.dependencies import get_current_user
from app.services import player_action_service, game_service
from app.models.player_actions import (
    WildChildChooseModelRequest, WildChildChooseModelResponse,
    WildChildStatusResponse, WildChildAvailableModelsResponse
)

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
    if not player_action_service.is_wild_child(game_id, wild_child_id):
        raise HTTPException(
            status_code=403,
            detail="Solo el Niño Salvaje puede acceder a esta información"
        )
    
    status_info = player_action_service.get_wild_child_status(game_id, wild_child_id)
    
    if not status_info:
        raise HTTPException(
            status_code=404,
            detail="No se pudo obtener información del Niño Salvaje"
        )
    
    return WildChildStatusResponse(
        success=True,
        message="Estado del Niño Salvaje obtenido correctamente",
        has_model=status_info.get("has_model", False),
        model_player_id=status_info.get("model_player_id"),
        model_username=status_info.get("model_username"),
        is_transformed=status_info.get("is_transformed", False),
        current_role=status_info.get("current_role", "wild_child")
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
    if not player_action_service.is_wild_child(game_id, wild_child_id):
        raise HTTPException(
            status_code=403,
            detail="Solo el Niño Salvaje puede acceder a esta información"
        )
    
    available_models = player_action_service.get_available_models_for_wild_child(game_id, wild_child_id)
    
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
    if not player_action_service.can_wild_child_choose_model(game_id, wild_child_id):
        raise HTTPException(
            status_code=403,
            detail="No puedes elegir un modelo en este momento"
        )
    
    # Obtener información del modelo elegido
    game = game_service.get_game(game_id)
    model_username = None
    if game:
        for player in game.players:
            if player.id == request.model_player_id:
                model_username = player.username
                break
    
    if not model_username:
        raise HTTPException(
            status_code=400,
            detail="El jugador elegido como modelo no existe"
        )
    
    # Realizar la elección
    updated_game = player_action_service.wild_child_choose_model(
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
    
    can_choose = player_action_service.can_wild_child_choose_model(game_id, wild_child_id)
    
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
    transformation_info = player_action_service.get_wild_child_transformation_info(game_id, wild_child_id)
    
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
    
    transformations = player_action_service.check_wild_child_transformation(game_id, dead_player_id)
    
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
    if not game or user_id not in game.roles:
        raise HTTPException(
            status_code=404,
            detail="Partida o jugador no encontrado"
        )
    
    user_role = game.roles[user_id]
    if user_role.role != "warewolf" or not user_role.is_alive:
        raise HTTPException(
            status_code=403,
            detail="Solo los hombres lobo pueden acceder a esta información"
        )
    
    # Buscar Niños Salvajes transformados recientemente
    new_werewolves = []
    for player_id, role_info in game.roles.items():
        if (role_info.role == "warewolf" and 
            role_info.has_transformed and
            player_id != user_id):
            
            # Obtener nombre del jugador
            for player in game.players:
                if player.id == player_id:
                    new_werewolves.append({
                        "id": player_id,
                        "username": player.username,
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
    
    success = player_action_service.initialize_wild_child(game_id, wild_child_id)
    
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
    transformations = player_action_service.process_wild_child_death_check(game_id)
    
    return {
        "success": True,
        "transformations": transformations,
        "message": f"Se procesaron {len(transformations)} verificaciones de transformación"
    }

# routes_witch.py
# Endpoints específicos para las acciones de la Bruja

from fastapi import APIRouter, HTTPException, Depends
from app.core.dependencies import get_current_user
from app.services import player_action_service, game_service
from app.models.player_actions import (
    WitchHealRequest, WitchHealResponse,
    WitchPoisonRequest, WitchPoisonResponse,
    WitchNightInfoResponse
)

router = APIRouter(prefix="/witch", tags=["witch"])


@router.get("/night-info/{game_id}", response_model=WitchNightInfoResponse)
async def get_witch_night_info(
    game_id: str,
    current_user = Depends(get_current_user)
):
    """
    Obtiene información nocturna para la bruja: quién fue atacado y qué pociones tiene disponibles.
    """
    witch_id = current_user.id
    
    # Verificar que el jugador es la bruja
    if not player_action_service.is_witch(game_id, witch_id):
        raise HTTPException(
            status_code=403,
            detail="Solo la bruja puede acceder a esta información"
        )
    
    night_info = player_action_service.get_witch_night_info(game_id, witch_id)
    
    if not night_info:
        raise HTTPException(
            status_code=404,
            detail="No se pudo obtener información de la partida"
        )
    
    return WitchNightInfoResponse(
        success=True,
        message="Información nocturna obtenida correctamente",
        attacked_player_id=night_info.get("attacked_player_id"),
        attacked_username=night_info.get("attacked_username"),
        can_heal=night_info.get("can_heal", False),
        can_poison=night_info.get("can_poison", False)
    )


@router.post("/heal", response_model=WitchHealResponse)
async def witch_heal_victim(
    game_id: str,
    request: WitchHealRequest,
    current_user = Depends(get_current_user)
):
    """
    Permite a la bruja usar su poción de curación para salvar a la víctima del ataque de los lobos.
    """
    witch_id = current_user.id
    
    # Verificar que el jugador es la bruja y puede curar
    if not player_action_service.can_witch_heal(game_id, witch_id):
        raise HTTPException(
            status_code=403,
            detail="No puedes usar la poción de curación en este momento"
        )
    
    # Verificar que el objetivo es realmente la víctima del ataque
    attack_victim = player_action_service.get_warewolf_attack_victim(game_id)
    if not attack_victim or attack_victim != request.target_id:
        raise HTTPException(
            status_code=400,
            detail="Solo puedes curar a la víctima del ataque de los hombres lobo"
        )
    
    # Obtener información del jugador curado
    game = game_service.get_game(game_id)
    healed_username = None
    if game:
        for player in game.players:
            if player.id == request.target_id:
                healed_username = player.username
                break
    
    # Realizar la curación
    updated_game = player_action_service.witch_heal_victim(
        game_id, witch_id, request.target_id
    )
    
    if not updated_game:
        raise HTTPException(
            status_code=400,
            detail="No se pudo realizar la curación"
        )
    
    return WitchHealResponse(
        success=True,
        message=f"Has usado tu poción de curación para salvar a {healed_username or request.target_id}",
        healed_player_id=request.target_id,
        healed_username=healed_username or "Jugador desconocido"
    )


@router.post("/poison", response_model=WitchPoisonResponse)
async def witch_poison_player(
    game_id: str,
    request: WitchPoisonRequest,
    current_user = Depends(get_current_user)
):
    """
    Permite a la bruja usar su poción de veneno para eliminar a un jugador.
    """
    witch_id = current_user.id
    
    # Verificar que el jugador es la bruja y puede envenenar
    if not player_action_service.can_witch_poison(game_id, witch_id):
        raise HTTPException(
            status_code=403,
            detail="No puedes usar la poción de veneno en este momento"
        )
    
    # Obtener información del jugador envenenado
    game = game_service.get_game(game_id)
    poisoned_username = None
    if game:
        for player in game.players:
            if player.id == request.target_id:
                poisoned_username = player.username
                break
    
    # Realizar el envenenamiento
    updated_game = player_action_service.witch_poison_player(
        game_id, witch_id, request.target_id
    )
    
    if not updated_game:
        raise HTTPException(
            status_code=400,
            detail="No se pudo realizar el envenenamiento"
        )
    
    return WitchPoisonResponse(
        success=True,
        message=f"Has usado tu poción de veneno contra {poisoned_username or request.target_id}",
        poisoned_player_id=request.target_id,
        poisoned_username=poisoned_username or "Jugador desconocido"
    )


@router.get("/can-heal/{game_id}")
async def check_can_heal(
    game_id: str,
    current_user = Depends(get_current_user)
):
    """
    Verifica si la bruja puede usar su poción de curación.
    """
    witch_id = current_user.id
    
    can_heal = player_action_service.can_witch_heal(game_id, witch_id)
    
    return {
        "success": True,
        "can_heal": can_heal,
        "message": "Puedes usar la poción de curación" if can_heal else "No puedes usar la poción de curación"
    }


@router.get("/can-poison/{game_id}")
async def check_can_poison(
    game_id: str,
    current_user = Depends(get_current_user)
):
    """
    Verifica si la bruja puede usar su poción de veneno.
    """
    witch_id = current_user.id
    
    can_poison = player_action_service.can_witch_poison(game_id, witch_id)
    
    return {
        "success": True,
        "can_poison": can_poison,
        "message": "Puedes usar la poción de veneno" if can_poison else "No puedes usar la poción de veneno"
    }


@router.get("/poison-targets/{game_id}")
async def get_poison_targets(
    game_id: str,
    current_user = Depends(get_current_user)
):
    """
    Obtiene la lista de jugadores que la bruja puede envenenar.
    """
    witch_id = current_user.id
    
    # Verificar que el jugador es la bruja
    if not player_action_service.is_witch(game_id, witch_id):
        raise HTTPException(
            status_code=403,
            detail="Solo la bruja puede acceder a esta información"
        )
    
    targets = player_action_service.get_witch_poison_targets(game_id, witch_id)
    
    return {
        "success": True,
        "targets": targets,
        "message": f"Se encontraron {len(targets)} objetivos disponibles"
    }


@router.get("/attack-victim/{game_id}")
async def get_attack_victim(
    game_id: str,
    current_user = Depends(get_current_user)
):
    """
    Obtiene información sobre el jugador atacado por los hombres lobo esta noche.
    """
    witch_id = current_user.id
    
    # Verificar que el jugador es la bruja
    if not player_action_service.is_witch(game_id, witch_id):
        raise HTTPException(
            status_code=403,
            detail="Solo la bruja puede acceder a esta información"
        )
    
    victim_id = player_action_service.get_warewolf_attack_victim(game_id)
    
    return {
        "success": True,
        "victim_id": victim_id,
        "message": "Víctima del ataque obtenida" if victim_id else "No hay víctima del ataque"
    }


@router.post("/initialize-potions/{game_id}")
async def initialize_potions(
    game_id: str,
    current_user = Depends(get_current_user)
):
    """
    Inicializa las pociones de la bruja al comienzo del juego.
    """
    witch_id = current_user.id
    
    success = player_action_service.initialize_witch_potions(game_id, witch_id)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="No se pudieron inicializar las pociones"
        )
    
    return {
        "success": True,
        "message": "Pociones inicializadas correctamente"
    }

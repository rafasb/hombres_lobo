"""
Rutas de API para las acciones de los jugadores durante las partidas.
Incluye endpoints para que los jugadores realicen sus acciones específicas según su rol.
Requiere autenticación JWT para acceder.
"""

from fastapi import APIRouter, HTTPException, Depends
from app.models.player_actions import (
    WarewolfAttackRequest,
    PlayerInfo,
    WarewolfAttackResponse,
)
from app.services.player_action_service import (
    warewolf_attack,
    get_warewolf_attack_consensus,
    get_alive_players,
    get_non_warewolf_players,
    can_warewolf_act,
)
from app.core.dependencies import get_current_user
from typing import List, Dict, Optional

router = APIRouter()


@router.post("/games/{game_id}/warewolf-attack", response_model=WarewolfAttackResponse)
def warewolf_select_target(
    game_id: str,
    attack_request: WarewolfAttackRequest,
    user=Depends(get_current_user)
):
    """
    Permite a un hombre lobo seleccionar a un aldeano para devorar durante la fase nocturna.
    
    Args:
        game_id: ID de la partida
        attack_request: Contiene el ID del jugador objetivo
        user: Usuario actual (debe ser un hombre lobo)
    
    Returns:
        Respuesta con el resultado de la acción y consenso si lo hay
    """
    # Verificar si el jugador puede actuar como hombre lobo
    if not can_warewolf_act(game_id, user.id):
        raise HTTPException(
            status_code=400,
            detail="No puedes realizar esta acción en este momento"
        )
    
    # Realizar el ataque
    updated_game = warewolf_attack(game_id, user.id, attack_request.target_id)
    if not updated_game:
        raise HTTPException(
            status_code=400,
            detail="No se pudo realizar el ataque. Verifica que el objetivo sea válido."
        )
    
    # Verificar si hay consenso entre los hombres lobo
    consensus_target = get_warewolf_attack_consensus(game_id)
    
    response = WarewolfAttackResponse(
        success=True,
        message="Tu voto de ataque ha sido registrado correctamente",
        consensus_target=consensus_target
    )
    
    if consensus_target:
        response.message += ". Los hombres lobo han llegado a un consenso."
    
    return response


@router.get("/games/{game_id}/warewolf-targets", response_model=List[PlayerInfo])
def get_warewolf_targets(game_id: str, user=Depends(get_current_user)):
    """
    Obtiene la lista de jugadores que pueden ser atacados por los hombres lobo.
    
    Args:
        game_id: ID de la partida
        user: Usuario actual (debe ser un hombre lobo)
    
    Returns:
        Lista de jugadores que no son hombres lobo y están vivos
    """
    # Verificar si el jugador puede actuar como hombre lobo
    if not can_warewolf_act(game_id, user.id):
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para ver esta información"
        )
    
    targets = get_non_warewolf_players(game_id)
    return [PlayerInfo(**target) for target in targets]


@router.get("/games/{game_id}/alive-players", response_model=List[PlayerInfo])
def get_alive_players_in_game(game_id: str, user=Depends(get_current_user)):
    """
    Obtiene la lista de todos los jugadores vivos en la partida.
    
    Args:
        game_id: ID de la partida
        user: Usuario actual (debe estar en la partida)
    
    Returns:
        Lista de todos los jugadores vivos
    """
    # Verificar que el usuario esté en la partida
    from app.services.game_service import get_game
    game = get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Partida no encontrada")
    
    # Verificar que el usuario está en la partida
    user_in_game = any(player.id == user.id for player in game.players)
    if not user_in_game:
        raise HTTPException(
            status_code=403,
            detail="No estás participando en esta partida"
        )
    
    alive_players = get_alive_players(game_id)
    return [PlayerInfo(**player) for player in alive_players]


@router.get("/games/{game_id}/warewolf-consensus", response_model=Dict[str, Optional[str]])
def get_warewolf_consensus(game_id: str, user=Depends(get_current_user)):
    """
    Verifica si los hombres lobo han llegado a un consenso sobre a quién atacar.
    
    Args:
        game_id: ID de la partida
        user: Usuario actual (debe ser un hombre lobo)
    
    Returns:
        Diccionario con el ID del objetivo consensuado o None
    """
    # Verificar si el jugador puede ver esta información
    if not can_warewolf_act(game_id, user.id):
        # También permitir si es hombre lobo que ya actuó esta noche
        from app.services.game_service import get_game
        game = get_game(game_id)
        if not game or user.id not in game.roles:
            raise HTTPException(status_code=403, detail="No tienes permisos para ver esta información")
        
        user_role = game.roles[user.id]
        if user_role.role.value != "warewolf" or not user_role.is_alive:
            raise HTTPException(status_code=403, detail="No tienes permisos para ver esta información")
    
    consensus_target = get_warewolf_attack_consensus(game_id)
    return {"consensus_target": consensus_target}


@router.get("/games/{game_id}/can-warewolf-act", response_model=Dict[str, bool])
def check_warewolf_can_act(game_id: str, user=Depends(get_current_user)):
    """
    Verifica si el usuario puede realizar una acción como hombre lobo.
    
    Args:
        game_id: ID de la partida
        user: Usuario actual
    
    Returns:
        Diccionario indicando si puede actuar
    """
    can_act = can_warewolf_act(game_id, user.id)
    return {"can_act": can_act}

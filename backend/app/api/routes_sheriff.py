"""
Rutas de API para las acciones del Alguacil durante las partidas.
Incluye endpoints específicos para desempatar votaciones y elegir sucesor.
Requiere autenticación JWT para acceder.
"""

from fastapi import APIRouter, HTTPException, Depends
from app.models.player_actions import (
    SheriffTiebreakerRequest,
    SheriffSuccessorRequest,
    SheriffTiebreakerResponse,
    SheriffSuccessorResponse,
    PlayerInfo,
)
from app.services.player_action_service import (
    is_sheriff,
    can_sheriff_break_tie,
    has_day_vote_tie,
    sheriff_break_tie,
    get_tied_players_info,
    can_sheriff_choose_successor,
    sheriff_choose_successor,
    get_sheriff_eligible_successors,
)
from app.core.dependencies import get_current_user
from typing import List, Dict

router = APIRouter()


@router.post("/games/{game_id}/sheriff-tiebreaker", response_model=SheriffTiebreakerResponse)
def break_voting_tie(
    game_id: str,
    tiebreaker_request: SheriffTiebreakerRequest,
    user=Depends(get_current_user)
):
    """
    Permite al alguacil desempatar una votación diurna eligiendo quién será eliminado.
    
    Args:
        game_id: ID de la partida
        tiebreaker_request: Contiene el ID del jugador elegido para eliminación
        user: Usuario actual (debe ser el alguacil)
    
    Returns:
        Respuesta con el resultado del desempate
    """
    # Verificar si el jugador es alguacil y puede desempatar
    if not can_sheriff_break_tie(game_id, user.id):
        raise HTTPException(
            status_code=400,
            detail="No puedes desempatar la votación en este momento"
        )
    
    # Realizar el desempate
    updated_game = sheriff_break_tie(game_id, user.id, tiebreaker_request.target_id)
    if not updated_game:
        raise HTTPException(
            status_code=400,
            detail="No se pudo resolver el empate. Verifica que el jugador elegido esté entre los empatados."
        )
    
    # Buscar información del jugador eliminado
    eliminated_username = None
    for player in updated_game.players:
        if player.id == tiebreaker_request.target_id:
            eliminated_username = player.username
            break
    
    if not eliminated_username:
        raise HTTPException(
            status_code=400,
            detail="No se pudo encontrar información del jugador eliminado"
        )
    
    response = SheriffTiebreakerResponse(
        success=True,
        message=f"Has decidido el empate. {eliminated_username} ha sido eliminado.",
        eliminated_player_id=tiebreaker_request.target_id,
        eliminated_username=eliminated_username
    )
    
    return response


@router.get("/games/{game_id}/tied-players", response_model=List[PlayerInfo])
def get_tied_players(game_id: str, user=Depends(get_current_user)):
    """
    Obtiene la lista de jugadores empatados en la votación diurna.
    
    Args:
        game_id: ID de la partida
        user: Usuario actual (debe ser el alguacil)
    
    Returns:
        Lista de jugadores empatados en la votación
    """
    # Verificar si el jugador es alguacil
    if not is_sheriff(game_id, user.id):
        raise HTTPException(
            status_code=403,
            detail="Solo el alguacil puede ver esta información"
        )
    
    tied_players = get_tied_players_info(game_id)
    return [PlayerInfo(**player) for player in tied_players]


@router.get("/games/{game_id}/can-sheriff-break-tie", response_model=Dict[str, bool])
def check_can_break_tie(game_id: str, user=Depends(get_current_user)):
    """
    Verifica si el alguacil puede desempatar la votación actual.
    
    Args:
        game_id: ID de la partida
        user: Usuario actual
    
    Returns:
        Diccionario indicando si puede desempatar
    """
    can_break = can_sheriff_break_tie(game_id, user.id)
    return {"can_break_tie": can_break}


@router.post("/games/{game_id}/sheriff-successor", response_model=SheriffSuccessorResponse)
def choose_successor(
    game_id: str,
    successor_request: SheriffSuccessorRequest,
    user=Depends(get_current_user)
):
    """
    Permite al alguacil elegir a su sucesor antes de morir.
    
    Args:
        game_id: ID de la partida
        successor_request: Contiene el ID del jugador elegido como sucesor
        user: Usuario actual (debe ser el alguacil)
    
    Returns:
        Respuesta con el resultado de la elección de sucesor
    """
    # Verificar si el jugador puede elegir sucesor
    if not can_sheriff_choose_successor(game_id, user.id):
        raise HTTPException(
            status_code=400,
            detail="No puedes elegir sucesor en este momento"
        )
    
    # Elegir al sucesor
    updated_game = sheriff_choose_successor(game_id, user.id, successor_request.successor_id)
    if not updated_game:
        raise HTTPException(
            status_code=400,
            detail="No se pudo elegir al sucesor. Verifica que el jugador elegido sea válido."
        )
    
    # Buscar información del sucesor
    successor_username = None
    for player in updated_game.players:
        if player.id == successor_request.successor_id:
            successor_username = player.username
            break
    
    if not successor_username:
        raise HTTPException(
            status_code=400,
            detail="No se pudo encontrar información del sucesor"
        )
    
    response = SheriffSuccessorResponse(
        success=True,
        message=f"Has elegido a {successor_username} como tu sucesor.",
        successor_id=successor_request.successor_id,
        successor_username=successor_username
    )
    
    return response


@router.get("/games/{game_id}/sheriff-successor-candidates", response_model=List[PlayerInfo])
def get_successor_candidates(game_id: str, user=Depends(get_current_user)):
    """
    Obtiene la lista de jugadores que pueden ser elegidos como sucesores del alguacil.
    
    Args:
        game_id: ID de la partida
        user: Usuario actual (debe ser el alguacil)
    
    Returns:
        Lista de jugadores vivos que pueden ser sucesores
    """
    # Verificar si el jugador puede elegir sucesor
    if not can_sheriff_choose_successor(game_id, user.id):
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para ver esta información"
        )
    
    eligible_successors = get_sheriff_eligible_successors(game_id, user.id)
    return [PlayerInfo(**successor) for successor in eligible_successors]


@router.get("/games/{game_id}/can-choose-successor", response_model=Dict[str, bool])
def check_can_choose_successor(game_id: str, user=Depends(get_current_user)):
    """
    Verifica si el alguacil puede elegir un sucesor.
    
    Args:
        game_id: ID de la partida
        user: Usuario actual
    
    Returns:
        Diccionario indicando si puede elegir sucesor
    """
    can_choose = can_sheriff_choose_successor(game_id, user.id)
    return {"can_choose_successor": can_choose}


@router.get("/games/{game_id}/is-sheriff", response_model=Dict[str, bool])
def check_is_sheriff(game_id: str, user=Depends(get_current_user)):
    """
    Verifica si el usuario es el alguacil de la partida.
    
    Args:
        game_id: ID de la partida
        user: Usuario actual
    
    Returns:
        Diccionario indicando si es el alguacil
    """
    sheriff_status = is_sheriff(game_id, user.id)
    return {"is_sheriff": sheriff_status}


@router.get("/games/{game_id}/has-vote-tie", response_model=Dict[str, bool])
def check_has_vote_tie(game_id: str, user=Depends(get_current_user)):
    """
    Verifica si hay empate en la votación diurna actual.
    
    Args:
        game_id: ID de la partida
        user: Usuario actual (debe ser el alguacil)
    
    Returns:
        Diccionario indicando si hay empate en la votación
    """
    # Verificar si el jugador es alguacil
    if not is_sheriff(game_id, user.id):
        raise HTTPException(
            status_code=403,
            detail="Solo el alguacil puede ver esta información"
        )
    
    has_tie = has_day_vote_tie(game_id)
    return {"has_tie": has_tie}

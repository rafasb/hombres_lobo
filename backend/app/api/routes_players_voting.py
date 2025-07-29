"""
Rutas de API para las acciones de votación de los jugadores durante las partidas.
Incluye endpoints específicos para el sistema de votación diurna.
Requiere autenticación JWT para acceder.
"""

from fastapi import APIRouter, HTTPException, Depends
from app.models.player_actions import (
    DayVoteRequest,
    PlayerInfo,
    VoteCount,
    DayVoteResponse,
)
from app.services.player_action_service import (
    day_vote,
    get_day_vote_counts,
    can_player_vote,
    get_voting_eligible_players,
    get_player_vote,
    get_voting_summary,
)
from app.core.dependencies import get_current_user
from typing import List, Dict, Optional, Any

router = APIRouter()


@router.post("/games/{game_id}/day-vote", response_model=DayVoteResponse)
def cast_day_vote(
    game_id: str,
    vote_request: DayVoteRequest,
    user=Depends(get_current_user)
):
    """
    Permite a un jugador vivo votar para eliminar a otro jugador durante la fase diurna.
    
    Args:
        game_id: ID de la partida
        vote_request: Contiene el ID del jugador objetivo
        user: Usuario actual (debe estar vivo)
    
    Returns:
        Respuesta con el resultado de la votación y resumen actual
    """
    # Verificar si el jugador puede votar
    if not can_player_vote(game_id, user.id):
        raise HTTPException(
            status_code=400,
            detail="No puedes votar en este momento"
        )
    
    # Realizar el voto
    updated_game = day_vote(game_id, user.id, vote_request.target_id)
    if not updated_game:
        raise HTTPException(
            status_code=400,
            detail="No se pudo registrar el voto. Verifica que el objetivo sea válido."
        )
    
    # Obtener resumen de votación
    vote_summary = get_voting_summary(game_id)
    vote_counts_data = get_day_vote_counts(game_id)
    
    # Convertir a formato de respuesta
    vote_counts = [
        VoteCount(**vote_data) for vote_data in vote_counts_data
    ]
    
    response = DayVoteResponse(
        success=True,
        message="Tu voto ha sido registrado correctamente",
        vote_counts=vote_counts,
        total_votes=vote_summary.get("total_votes", 0),
        total_players=vote_summary.get("total_players", 0)
    )
    
    return response


@router.get("/games/{game_id}/voting-targets", response_model=List[PlayerInfo])
def get_voting_targets(game_id: str, user=Depends(get_current_user)):
    """
    Obtiene la lista de jugadores que pueden ser votados para eliminación.
    
    Args:
        game_id: ID de la partida
        user: Usuario actual (debe estar en la partida)
    
    Returns:
        Lista de jugadores vivos que pueden ser votados
    """
    # Verificar que el usuario pueda votar
    if not can_player_vote(game_id, user.id):
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para ver esta información"
        )
    
    eligible_players = get_voting_eligible_players(game_id)
    return [PlayerInfo(**player) for player in eligible_players]


@router.get("/games/{game_id}/vote-counts", response_model=List[VoteCount])
def get_current_vote_counts(game_id: str, user=Depends(get_current_user)):
    """
    Obtiene el recuento actual de votos diurnos.
    
    Args:
        game_id: ID de la partida
        user: Usuario actual (debe estar en la partida)
    
    Returns:
        Lista con el recuento de votos por jugador
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
    
    vote_counts_data = get_day_vote_counts(game_id)
    return [VoteCount(**vote_data) for vote_data in vote_counts_data]


@router.get("/games/{game_id}/my-vote", response_model=Dict[str, Optional[str]])
def get_my_vote(game_id: str, user=Depends(get_current_user)):
    """
    Obtiene el voto actual del usuario.
    
    Args:
        game_id: ID de la partida
        user: Usuario actual
    
    Returns:
        Diccionario con el ID del jugador votado o None
    """
    # Verificar que el usuario pueda votar
    if not can_player_vote(game_id, user.id):
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para ver esta información"
        )
    
    voted_player_id = get_player_vote(game_id, user.id)
    return {"voted_player_id": voted_player_id}


@router.get("/games/{game_id}/voting-summary", response_model=Dict[str, Any])
def get_voting_summary_endpoint(game_id: str, user=Depends(get_current_user)):
    """
    Obtiene un resumen completo de la votación actual.
    
    Args:
        game_id: ID de la partida
        user: Usuario actual (debe estar en la partida)
    
    Returns:
        Resumen completo de la votación
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
    
    return get_voting_summary(game_id)


@router.get("/games/{game_id}/can-vote", response_model=Dict[str, bool])
def check_can_vote(game_id: str, user=Depends(get_current_user)):
    """
    Verifica si el usuario puede votar durante la fase diurna.
    
    Args:
        game_id: ID de la partida
        user: Usuario actual
    
    Returns:
        Diccionario indicando si puede votar
    """
    can_vote = can_player_vote(game_id, user.id)
    return {"can_vote": can_vote}

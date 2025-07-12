"""
Rutas de API para la gestión de partidas.
Incluye endpoints para crear, consultar y listar partidas.
Requiere autenticación JWT para acceder.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from app.models.game import Game, GameCreate, GameStatus
from app.services.game_service import (
    create_game,
    get_game,
    get_all_games,
    update_game_params,
    change_game_status,
    creator_delete_game,
)
from app.core.dependencies import get_current_user
import uuid

router = APIRouter()


@router.post("/games", response_model=Game)
def create_new_game(game: GameCreate, user=Depends(get_current_user)):
    new_game = Game(
        id=str(uuid.uuid4()),
        name=game.name,
        creator_id=game.creator_id,
        players=[],
        roles={},
        status=GameStatus.WAITING,
        max_players=game.max_players,
    )
    create_game(new_game)
    return new_game


@router.get("/games/{game_id}", response_model=Game)
def get_game_by_id(game_id: str, user=Depends(get_current_user)):
    game = get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Partida no encontrada")
    return game


@router.get("/games", response_model=list[Game])
def list_games(user=Depends(get_current_user)):
    return get_all_games()


@router.post("/games/{game_id}/leave")
def leave_game_endpoint(game_id: str, user=Depends(get_current_user)):
    """Permite que un usuario autenticado abandone una partida si aún no ha comenzado."""
    from app.services.game_service import leave_game

    if leave_game(game_id, user.id):
        return {"detail": "Has abandonado la partida"}
    raise HTTPException(
        status_code=400,
        detail="No puedes abandonar la partida (no eres jugador o la partida ya ha comenzado)",
    )


@router.put("/games/{game_id}", response_model=Game)
def update_game(game_id: str, data: dict = Body(...), user=Depends(get_current_user)):
    """Permite al creador modificar nombre, max_players y roles antes de que comience la partida."""
    name = data.get("name")
    max_players = data.get("max_players")
    roles = data.get("roles")
    updated = update_game_params(game_id, user.id, name, max_players, roles)
    if updated:
        return updated
    raise HTTPException(
        status_code=403,
        detail="No tienes permisos o la partida ya ha comenzado",
    )


@router.put("/games/{game_id}/status", response_model=Game)
def update_game_status(
    game_id: str, status: GameStatus = Body(...), user=Depends(get_current_user)
):
    """Permite al creador iniciar, pausar, avanzar fase o detener la partida."""
    updated = change_game_status(game_id, user.id, status)
    if updated:
        return updated
    raise HTTPException(
        status_code=403, detail="No tienes permisos o transición de estado no permitida"
    )


@router.delete("/games/{game_id}")
def delete_game_by_creator(game_id: str, user=Depends(get_current_user)):
    """Permite al creador eliminar la partida si está en estado WAITING o PAUSED."""
    if creator_delete_game(game_id, user.id):
        return {"detail": "Partida eliminada"}
    raise HTTPException(
        status_code=403, detail="No tienes permisos o la partida no puede eliminarse"
    )

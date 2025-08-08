"""
Rutas de API para la gestión de partidas.
Incluye endpoints para crear, consultar y listar partidas.
Requiere autenticación JWT para acceder.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from app.models.game_and_roles import Game, GameCreate, GameStatus
from app.models.user import UserRole
from app.services.game_service import (
    create_game,
    get_game,
    get_all_games,
    update_game_params,
    creator_delete_game,
    join_game,
)
from app.services.game_flow_service import (
    change_game_status,
    assign_roles,
)
from app.core.dependencies import get_current_user
from app.database import game_to_response
import uuid

router = APIRouter()


@router.post("/games")
def create_new_game(game: GameCreate, user=Depends(get_current_user)):
    new_game = Game(
        id=str(uuid.uuid4()),
        name=game.name,
        creator_id=game.creator_id,
        players=[user.id],  # Solo almacenamos el ID del creador
        roles={},
        status=GameStatus.WAITING,
        max_players=game.max_players,
    )
    create_game(new_game)
    return game_to_response(new_game)


@router.get("/games/{game_id}")
def get_game_by_id(game_id: str, user=Depends(get_current_user)):
    game = get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Partida no encontrada")
    return game_to_response(game)


@router.get("/games")
def list_games(user=Depends(get_current_user)):
    games = get_all_games()
    return [game_to_response(game) for game in games]


@router.post("/games/{game_id}/join")
def join_game_endpoint(game_id: str, user=Depends(get_current_user)):
    """Permite que un usuario autenticado se una a una partida que esté esperando jugadores."""
    if join_game(game_id, user):
        return {"detail": "Te has unido a la partida exitosamente"}
    raise HTTPException(
        status_code=400,
        detail="No puedes unirte a la partida (partida llena, ya comenzó, no existe, o ya eres jugador)",
    )


@router.post("/games/{game_id}/assign-roles")
def assign_roles_endpoint(game_id: str, user=Depends(get_current_user)):
    """Permite al creador o admin iniciar el reparto de roles y comenzar la partida."""
    is_admin = user.role == UserRole.ADMIN
    game = assign_roles(game_id, user.id, is_admin)
    if game:
        return game_to_response(game)
    raise HTTPException(
        status_code=400,
        detail="No puedes iniciar el reparto de roles (no tienes permisos, partida ya iniciada, o faltan jugadores)",
    )


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


@router.put("/games/{game_id}")
def update_game(game_id: str, data: dict = Body(...), user=Depends(get_current_user)):
    """Permite al creador o admin modificar nombre, max_players y roles antes de que comience la partida."""
    name = data.get("name")
    max_players = data.get("max_players")
    roles = data.get("roles")
    is_admin = user.role == UserRole.ADMIN
    updated = update_game_params(game_id, user.id, name, max_players, roles, is_admin)
    if updated:
        return game_to_response(updated)
    raise HTTPException(
        status_code=403,
        detail="No tienes permisos o la partida ya ha comenzado",
    )


@router.put("/games/{game_id}/status")
def update_game_status(
    game_id: str, status: GameStatus = Body(...), user=Depends(get_current_user)
):
    """Permite al creador o admin iniciar, pausar, avanzar fase o detener la partida."""
    is_admin = user.role == UserRole.ADMIN
    updated = change_game_status(game_id, user.id, status, is_admin)
    if updated:
        return game_to_response(updated)
    raise HTTPException(
        status_code=403, detail="No tienes permisos o transición de estado no permitida"
    )


@router.delete("/games/{game_id}")
def delete_game_by_creator(game_id: str, user=Depends(get_current_user)):
    """Permite al creador o admin eliminar la partida si está en estado WAITING o PAUSED."""
    is_admin = user.role == UserRole.ADMIN
    if creator_delete_game(game_id, user.id, is_admin):
        return {"detail": "Partida eliminada"}
    raise HTTPException(
        status_code=403, detail="No tienes permisos o la partida no puede eliminarse"
    )

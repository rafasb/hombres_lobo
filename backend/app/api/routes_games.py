"""
Rutas de API para la gestión de partidas.
Incluye endpoints para crear, consultar y listar partidas.
Requiere autenticación JWT para acceder.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from app.models.game_and_roles import Game, GameCreate, GameStatus
from app.models.game_responses import (
    GameCreateResponse,
    GameGetResponse,
    GameListResponse,
    GameJoinResponse,
    GameLeaveResponse,
    GameRoleAssignmentResponse,
    GameUpdateResponse,
    GameStatusUpdateResponse,
    GameDeleteResponse
)
from app.models.user import UserRole, User
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
from app.core.dependencies import get_current_user, get_current_user_id
from app.database import game_to_game_response
import uuid

router = APIRouter(prefix="/games", tags=["games"])


@router.post("", response_model=GameCreateResponse)
def create_new_game(game: GameCreate, user=Depends(get_current_user)):
    new_game = Game(
        id=str(uuid.uuid4()),
        name=game.name,
        creator_id=game.creator_id,
        max_players=game.max_players,
        players=[user.id],  # Solo almacenamos el ID del creador
        roles={},
        status=GameStatus.WAITING
    )
    create_game(new_game)
    game_response = game_to_game_response(new_game)
    
    return GameCreateResponse(
        success=True,
        message=f"Partida '{game.name}' creada exitosamente",
        game=game_response
    )


@router.get("/{game_id}", response_model=GameGetResponse)
def get_game_by_id(game_id: str, user=Depends(get_current_user)):
    game = get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Partida no encontrada")
    
    game_response = game_to_game_response(game)
    return GameGetResponse(
        success=True,
        message="Partida obtenida exitosamente",
        game=game_response
    )


@router.get("", response_model=GameListResponse)
def list_games(user=Depends(get_current_user)):
    games = get_all_games()
    games_response = [game_to_game_response(game) for game in games]
    
    return GameListResponse(
        success=True,
        message="Lista de partidas obtenida exitosamente",
        games=games_response,
        total_games=len(games_response)
    )


@router.post("/{game_id}/join", response_model=GameJoinResponse)
def join_game_endpoint(game_id: str, user: User = Depends(get_current_user)):
    """Permite que un usuario autenticado se una a una partida que esté esperando jugadores."""
    user_id = user.id
    if join_game(game_id, user_id):
        # Obtener la partida actualizada
        updated_game = get_game(game_id)
        if updated_game:
            return GameJoinResponse(
                success=True,
                message="Te has unido a la partida exitosamente",
                game_id=game_id,
                current_players=len(updated_game.players),
                max_players=updated_game.max_players
            )
    
    raise HTTPException(
        status_code=400,
        detail="No puedes unirte a la partida (partida llena, ya comenzó, no existe, o ya eres jugador)",
    )


@router.post("/{game_id}/assign-roles", response_model=GameRoleAssignmentResponse)
def assign_roles_endpoint(game_id: str, user=Depends(get_current_user)):
    """Permite al creador o admin iniciar el reparto de roles y comenzar la partida."""
    is_admin = user.role == UserRole.ADMIN
    game = assign_roles(game_id, get_current_user_id(), is_admin)
    if game:
        game_response = game_to_game_response(game)
        
        # Contar roles asignados
        assigned_roles = sum(1 for role_info in game.roles.values() if role_info.role != "villager")
        total_players = len(game.players)
        
        return GameRoleAssignmentResponse(
            success=True,
            message="Roles asignados exitosamente",
            game=game_response,
            assigned_roles_count=assigned_roles,
            players_with_roles=total_players
        )
    
    raise HTTPException(
        status_code=400,
        detail="No puedes iniciar el reparto de roles (no tienes permisos, partida ya iniciada, o faltan jugadores)",
    )


@router.post("/{game_id}/leave", response_model=GameLeaveResponse)
def leave_game_endpoint(game_id: str, user=Depends(get_current_user)):
    """Permite que un usuario autenticado abandone una partida si aún no ha comenzado."""
    from app.services.game_service import leave_game

    if leave_game(game_id, user.id):
        # Obtener la partida actualizada para ver cuántos jugadores quedan
        updated_game = get_game(game_id)
        remaining_players = len(updated_game.players) if updated_game else 0
        
        return GameLeaveResponse(
            success=True,
            message="Has abandonado la partida",
            game_id=game_id,
            remaining_players=remaining_players
        )
    
    raise HTTPException(
        status_code=400,
        detail="No puedes abandonar la partida (no eres jugador o la partida ya ha comenzado)",
    )


@router.put("/{game_id}", response_model=GameUpdateResponse)
def update_game(game_id: str, data: dict = Body(...), user=Depends(get_current_user)):
    """Permite al creador o admin modificar nombre, max_players y roles antes de que comience la partida."""
    name = data.get("name")
    max_players = data.get("max_players")
    roles = data.get("roles")
    is_admin = user.role == UserRole.ADMIN
    
    updated = update_game_params(game_id, user.id, name, max_players, roles, is_admin)
    if updated:
        game_response = game_to_game_response(updated)
        
        # Determinar qué campos se actualizaron
        updated_fields = []
        if name is not None:
            updated_fields.append("name")
        if max_players is not None:
            updated_fields.append("max_players")
        if roles is not None:
            updated_fields.append("roles")
        
        return GameUpdateResponse(
            success=True,
            message="Partida actualizada exitosamente",
            game=game_response,
            updated_fields=updated_fields
        )
    
    raise HTTPException(
        status_code=403,
        detail="No tienes permisos o la partida ya ha comenzado",
    )


@router.put("/{game_id}/status", response_model=GameStatusUpdateResponse)
def update_game_status(
    game_id: str, status: GameStatus = Body(...), user=Depends(get_current_user)
):
    """Permite al creador o admin iniciar, pausar, avanzar fase o detener la partida."""
    is_admin = user.role == UserRole.ADMIN
    
    # Obtener estado previo
    current_game = get_game(game_id)
    previous_status = current_game.status.value if current_game else "unknown"
    
    updated = change_game_status(game_id, user.id, status, is_admin)
    if updated:
        game_response = game_to_game_response(updated)
        
        return GameStatusUpdateResponse(
            success=True,
            message=f"Estado de la partida cambiado de {previous_status} a {status.value}",
            game=game_response,
            previous_status=previous_status,
            new_status=status.value
        )
    
    raise HTTPException(
        status_code=403, detail="No tienes permisos o transición de estado no permitida"
    )


@router.delete("/{game_id}", response_model=GameDeleteResponse)
def delete_game_by_creator(game_id: str, user=Depends(get_current_user)):
    """Permite al creador o admin eliminar la partida si está en estado WAITING o PAUSED."""
    is_admin = user.role == UserRole.ADMIN
    
    if creator_delete_game(game_id, user.id, is_admin):
        return GameDeleteResponse(
            success=True,
            message="Partida eliminada exitosamente",
            deleted_game_id=game_id
        )
    
    raise HTTPException(
        status_code=403, detail="No tienes permisos o la partida no puede eliminarse"
    )

"""
Rutas de API para la gestión de usuarios administradores.
Incluye endpoints para gestión de usuarios (solo accesibles por admin).
"""

from fastapi import APIRouter, HTTPException, Body, Depends
from app.models.user import User, UserRole, UserStatus, UserUpdate
from app.models.game_and_roles import Game
from app.services.user_service import get_user, get_all_users, update_user
from app.services.game_service import delete_game, get_all_games
from app.core.dependencies import admin_required

router = APIRouter()

@router.get("/admin/users", response_model=list[User])
def admin_list_users(admin=Depends(admin_required)):
    return get_all_users()

@router.get("/admin/users/{user_id}", response_model=User)
def admin_get_user(user_id: str, admin=Depends(admin_required)):
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.put("/admin/users/{user_id}", response_model=User)
def admin_update_user(user_id: str, update: UserUpdate = Body(...), admin=Depends(admin_required)):
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    updated = update_user(user, update)
    return updated

@router.delete("/admin/users/{user_id}")
def admin_delete_user(user_id: str, admin=Depends(admin_required)):
    users = get_all_users()
    if user_id == admin.id and sum(1 for u in users if u.role == UserRole.ADMIN) == 1:
        raise HTTPException(status_code=400, detail="No puedes eliminarte si eres el único admin")
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user.status = UserStatus.BANNED
    update_user(user, UserUpdate())
    return {"detail": "Usuario eliminado (baneado)"}

@router.put("/admin/users/{user_id}/role", response_model=User)
def admin_update_user_role(user_id: str, role: UserRole, admin=Depends(admin_required)):
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user.role = role
    update_user(user, UserUpdate())
    return user

@router.delete("/admin/games/{game_id}")
def admin_delete_game(game_id: str, admin=Depends(admin_required)):
    """Elimina una partida por su id (solo admin)."""
    if delete_game(game_id):
        return {"detail": "Partida eliminada"}
    raise HTTPException(status_code=404, detail="Partida no encontrada")

@router.get("/admin/games", response_model=list[Game])
def admin_list_games(admin=Depends(admin_required)):
    """Consultar el estado de todas las partidas activas o históricas (solo admin)."""
    return get_all_games()

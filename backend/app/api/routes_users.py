"""
Rutas de API para la gestión de usuarios.
Incluye endpoints para consulta y edición de usuarios.
Todas las rutas requieren autenticación JWT.
Los endpoints de autenticación (registro y login) se han movido a routes_auth.py.
Las rutas de administración se han movido a routes_admin.py.

Actualizado para reflejar los cambios en el modelo de datos:
- UserStatus: eliminado 'inactive', añadido 'in_game'.
- User: añade los campos 'in_game' (bool) y 'game_id' (str|None).
- UserStatusUpdate: permite informar 'game_id' junto con el estado.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from app.models.user import UserAccessRole, UserUpdate, UserStatusUpdate
from app.models.user_responses import (
    UserProfileResponse,
    UsersListResponse,
    UserUpdateResponse,
    UserStatusUpdateResponse
)
from app.services.user_service import get_user, get_all_users, update_user, update_user_status
from app.core.dependencies import get_current_user, admin_required

router = APIRouter(prefix="/users",tags=["users"])

@router.get("/me", response_model=UserProfileResponse)
def get_my_profile(current_user=Depends(get_current_user)):
    """Obtiene los datos del usuario autenticado actual."""
    return UserProfileResponse(
        success=True,
        message="Perfil obtenido exitosamente",
        user=current_user
    )

@router.get("/{user_id}", response_model=UserProfileResponse)
def get_user_by_id(user_id: str, current_user=Depends(get_current_user)):
    """Obtiene los datos de un usuario específico por su ID."""
    # Verificar que solo puede ver su propio perfil o ser admin
    if current_user.role != UserAccessRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Solo puedes acceder a tu propio perfil")
    
    user_obj = get_user(user_id)
    if not user_obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return UserProfileResponse(
        success=True,
        message="Usuario obtenido exitosamente",
        user=user_obj
    )

@router.get("", response_model=UsersListResponse)
def list_users(admin=Depends(admin_required)):
    """Obtiene la lista completa de todos los usuarios registrados (solo administradores)."""
    """Solo los administradores pueden ver la lista completa de usuarios."""
    users = get_all_users()
    
    return UsersListResponse(
        success=True,
        message="Lista de usuarios obtenida exitosamente",
        users=users,
        total_users=len(users)
    )

@router.put("/me", response_model=UserUpdateResponse)
def update_my_profile(
    update: UserUpdate = Body(...),
    user=Depends(get_current_user)
):
    """Actualiza los datos del perfil del usuario autenticado actual."""
    updated = update_user(user, update)
    
    # Determinar qué campos se actualizaron basándose en los datos del request
    updated_fields = []
    update_dict = update.model_dump(exclude_unset=True)
    for field in update_dict.keys():
        if field in update_dict:  # Solo incluir campos que fueron enviados
            updated_fields.append(field)
    
    return UserUpdateResponse(
        success=True,
        message="Perfil actualizado exitosamente",
        user=updated,
        updated_fields=updated_fields
    )

@router.put("/{user_id}/status", response_model=UserStatusUpdateResponse)
def update_user_status_endpoint(
    user_id: str, 
    status_update: UserStatusUpdate = Body(...),
    current_user=Depends(get_current_user)
):
    """
    Actualiza el estado de un usuario específico.

    Estados disponibles:
    - active: Usuario activo y disponible
    - banned: Usuario bloqueado/baneado (solo administradores)
    - connected: Usuario conectado a la aplicación
    - disconnected: Usuario desconectado de la aplicación
    - in_game: Usuario en una partida activa (requiere game_id)

    El campo opcional 'game_id' permite asociar el usuario a una partida cuando el estado es 'in_game'.
    Solo administradores pueden cambiar estados a 'banned'.
    Los usuarios pueden cambiar su propio estado entre 'connected', 'disconnected' e 'in_game'.
    """
    # Verificar permisos
    if current_user.id != user_id and current_user.role != UserAccessRole.ADMIN:
        raise HTTPException(
            status_code=403, 
            detail="Solo puedes cambiar tu propio estado de conexión o ser administrador"
        )
    
    # Solo admins pueden banear usuarios
    if status_update.status.value == "banned" and current_user.role != UserAccessRole.ADMIN:
        raise HTTPException(
            status_code=403, 
            detail="Solo los administradores pueden banear usuarios"
        )
    
    # Verificar que el usuario existe
    target_user = get_user(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Validar coherencia entre estado y game_id
    if status_update.status == "in_game":
        if not status_update.game_id:
            raise HTTPException(status_code=422, detail="El campo 'game_id' es obligatorio cuando el estado es 'in_game'.")
    else:
        # Si el estado no es in_game, ignorar game_id
        status_update.game_id = None

    # Actualizar el estado
    updated_user, old_status = update_user_status(user_id, status_update)

    if not updated_user or old_status is None:
        raise HTTPException(status_code=500, detail="Error al actualizar el estado del usuario")

    return UserStatusUpdateResponse(
        success=True,
        message=f"Estado del usuario actualizado de '{old_status.value}' a '{status_update.status.value}'",
        user_id=user_id,
        old_status=old_status.value,
        new_status=status_update.status.value,
        updated_at=updated_user.updated_at.isoformat()
    )

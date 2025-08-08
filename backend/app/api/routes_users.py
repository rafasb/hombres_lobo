"""
Rutas de API para la gestión de usuarios y autenticación.
Incluye endpoints para registro, login, consulta y edición de usuarios.
Las rutas de consulta y listado requieren autenticación JWT.
Las rutas de administración se han movido a routes_admin.py.
"""

from fastapi import APIRouter, HTTPException, Form, status, Depends, Body
from app.models.user import User, UserRole, UserStatus, UserUpdate
from app.models.user_responses import (
    LoginResponse,
    RegisterResponse,
    UserProfileResponse,
    UsersListResponse,
    UserUpdateResponse
)
from app.services.user_service import create_user, get_user, get_all_users, update_user
from app.core.security import hash_password, verify_password, create_access_token
from app.core.dependencies import get_current_user, admin_required
import uuid

router = APIRouter()

@router.post("/register", response_model=RegisterResponse)
def register_user(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    hashed = hash_password(password)
    user = User(
        id=str(uuid.uuid4()),
        username=username,
        email=email,
        role=UserRole.PLAYER,
        status=UserStatus.ACTIVE,
        hashed_password=hashed
    )
    create_user(user)
    
    return RegisterResponse(
        success=True,
        message=f"Usuario '{username}' registrado exitosamente",
        user=user
    )

@router.post("/login", response_model=LoginResponse)
def login_user(username: str = Form(...), password: str = Form(...)):
    # Buscar usuario por username
    users = get_all_users()
    user = next((u for u in users if u.username == username), None)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
    
    # Generar token JWT
    token = create_access_token({"sub": user.id, "username": user.username, "role": user.role})
    
    return LoginResponse(
        success=True,
        message=f"Login exitoso para {username}",
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        role=user.role.value
    )

@router.get("/users/me", response_model=UserProfileResponse)
def get_my_profile(current_user=Depends(get_current_user)):
    """Obtiene los datos del usuario autenticado actual."""
    return UserProfileResponse(
        success=True,
        message="Perfil obtenido exitosamente",
        user=current_user
    )

@router.get("/users/{user_id}", response_model=UserProfileResponse)
def get_user_by_id(user_id: str, current_user=Depends(get_current_user)):
    # Verificar que solo puede ver su propio perfil o ser admin
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Solo puedes acceder a tu propio perfil")
    
    user_obj = get_user(user_id)
    if not user_obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return UserProfileResponse(
        success=True,
        message="Usuario obtenido exitosamente",
        user=user_obj
    )

@router.get("/users", response_model=UsersListResponse)
def list_users(admin=Depends(admin_required)):
    """Solo los administradores pueden ver la lista completa de usuarios."""
    users = get_all_users()
    
    return UsersListResponse(
        success=True,
        message="Lista de usuarios obtenida exitosamente",
        users=users,
        total_users=len(users)
    )

@router.put("/users/me", response_model=UserUpdateResponse)
def update_my_profile(update: UserUpdate = Body(...), user=Depends(get_current_user)):
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

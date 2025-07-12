"""
Rutas de API para la gestión de usuarios y autenticación.
Incluye endpoints para registro, login, consulta y edición de usuarios.
Las rutas de consulta y listado requieren autenticación JWT.
Las rutas de administración se han movido a routes_admin.py.
"""

from fastapi import APIRouter, HTTPException, Form, status, Depends, Body
from app.models.user import User, UserRole, UserStatus, UserUpdate
from app.services.user_service import create_user, get_user, get_all_users, update_user
from app.core.security import hash_password, verify_password, create_access_token
from app.core.dependencies import get_current_user, admin_required
import uuid

router = APIRouter()

@router.post("/register", response_model=User)
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
    return user

@router.post("/login")
def login_user(username: str = Form(...), password: str = Form(...)):
    # Buscar usuario por username
    users = get_all_users()
    user = next((u for u in users if u.username == username), None)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
    # Generar token JWT
    token = create_access_token({"sub": user.id, "username": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/users/{user_id}", response_model=User)
def get_user_by_id(user_id: str, current_user=Depends(get_current_user)):
    # Verificar que solo puede ver su propio perfil o ser admin
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Solo puedes acceder a tu propio perfil")
    
    user_obj = get_user(user_id)
    if not user_obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user_obj

@router.get("/users", response_model=list[User])
def list_users(admin=Depends(admin_required)):
    """Solo los administradores pueden ver la lista completa de usuarios."""
    return get_all_users()

@router.put("/users/me", response_model=User)
def update_my_profile(update: UserUpdate = Body(...), user=Depends(get_current_user)):
    updated = update_user(user, update)
    return updated

"""
Rutas de API para la gestión de usuarios y autenticación.
Incluye endpoints para registro, consulta y listado de usuarios.
"""

from fastapi import APIRouter, HTTPException, Form
from app.models.user import User, UserRole, UserStatus
from app.services.user_service import create_user, get_user, get_all_users
import uuid

router = APIRouter()

@router.post("/register", response_model=User)
def register_user(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    user = User(
        id=str(uuid.uuid4()),
        username=username,
        email=email,
        role=UserRole.PLAYER,
        status=UserStatus.ACTIVE,
        hashed_password=password  # Aquí debería ir el hash real
    )
    create_user(user)
    return user

@router.get("/users/{user_id}", response_model=User)
def get_user_by_id(user_id: str):
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.get("/users", response_model=list[User])
def list_users():
    return get_all_users()

"""
Módulo de servicios para la gestión de usuarios.
Incluye funciones para crear, obtener, actualizar y listar usuarios usando la base de datos JSON.
"""

from app.database import save_user, load_user, load_all_users
from app.models.user import User, UserUpdate, UserRole
from typing import Optional, List
from datetime import datetime, UTC
from app.core.security import hash_password

def create_user(user: User) -> None:
    users = load_all_users()
    if not users:
        user.role = UserRole.ADMIN  # Primer usuario es admin
    user.created_at = datetime.now(UTC)
    user.updated_at = datetime.now(UTC)
    # Solo hashear si no es ya un hash (evita doble hash)
    if not user.hashed_password.startswith('$2b$'):
        user.hashed_password = hash_password(user.hashed_password)
    save_user(user)

def update_user(user: User, update: UserUpdate) -> User:
    if update.email:
        user.email = update.email
    if update.password:
        user.hashed_password = hash_password(update.password)
    user.updated_at = datetime.now(UTC)
    save_user(user)
    return user

def get_user(user_id: str) -> Optional[User]:
    return load_user(user_id)

def get_all_users() -> List[User]:
    return load_all_users()

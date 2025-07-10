"""
Módulo de servicios para la gestión de usuarios.
Incluye funciones para crear, obtener y listar usuarios usando la base de datos JSON.
"""

from app.database import save_user, load_user, load_all_users
from app.models.user import User
from typing import Optional, List

def create_user(user: User) -> None:
    save_user(user)

def get_user(user_id: str) -> Optional[User]:
    return load_user(user_id)

def get_all_users() -> List[User]:
    return load_all_users()

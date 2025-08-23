"""
Módulo de servicios para la gestión de usuarios.
Incluye funciones para crear, obtener, actualizar y listar usuarios usando la base de datos JSON.
"""

from app.database import save_user, load_user, load_all_users, delete_user as db_delete_user
from app.models.user import User, UserUpdate, UserAccessRole, UserStatus, UserStatusUpdate
from typing import Optional, List
from datetime import datetime, UTC
from app.core.security import hash_password


class UserService:
    """Servicio para la gestión de usuarios."""
    
    @staticmethod
    def create_user(user: User) -> None:
        """Crea un nuevo usuario en la base de datos."""
        users = load_all_users()
        if not users:
            user.role = UserAccessRole.ADMIN  # Primer usuario es admin
        user.created_at = datetime.now(UTC)
        user.updated_at = datetime.now(UTC)
        # Solo hashear si no es ya un hash (evita doble hash)
        if not user.hashed_password.startswith('$2b$'):
            user.hashed_password = hash_password(user.hashed_password)
        save_user(user)

    @staticmethod
    def update_user(user: User, update: UserUpdate) -> User:
        """Actualiza los datos de un usuario existente."""
        if update.email:
            user.email = update.email
        if update.password:
            user.hashed_password = hash_password(update.password)
        user.updated_at = datetime.now(UTC)
        save_user(user)
        return user

    @staticmethod
    def get_user(user_id: str) -> Optional[User]:
        """Obtiene un usuario por su ID."""
        return load_user(user_id)

    @staticmethod
    def get_all_users() -> List[User]:
        """Obtiene todos los usuarios registrados."""
        return load_all_users()

    @staticmethod
    def delete_user(user_id: str) -> bool:
        """Elimina un usuario de la base de datos físicamente."""
        return db_delete_user(user_id)

    @staticmethod
    def update_user_status(user_id: str, status_update: UserStatusUpdate) -> tuple[User, UserStatus] | tuple[None, None]:
        """Actualiza el estado de un usuario y devuelve el usuario actualizado y el estado anterior."""
        user = load_user(user_id)
        if not user:
            return None, None
        
        old_status = user.status
        user.status = status_update.status
        user.updated_at = datetime.now(UTC)
        save_user(user)
        return user, old_status
    
    # Metodo para obtenet el nombre de usuario por ID
    @staticmethod
    def get_username_by_id(user_id: str) -> str:
        """Obtiene el nombre de usuario por su ID."""
        user = UserService.get_user(user_id)
        if user:
            return user.username
        else:
            # Si no se encuentra el usuario, retornar un nombre genérico o None
            return "unknown name"

# Funciones existentes mantenidas para compatibilidad durante la refactorización
def create_user(user: User) -> None:
    users = load_all_users()
    if not users:
        user.role = UserAccessRole.ADMIN  # Primer usuario es admin
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

def delete_user(user_id: str) -> bool:
    """Elimina un usuario de la base de datos físicamente."""
    return db_delete_user(user_id)

def update_user_status(user_id: str, status_update: UserStatusUpdate) -> tuple[User, UserStatus] | tuple[None, None]:
    """Actualiza el estado de un usuario y devuelve el usuario actualizado y el estado anterior."""
    user = load_user(user_id)
    if not user:
        return None, None
    
    old_status = user.status
    user.status = status_update.status
    user.updated_at = datetime.now(UTC)
    save_user(user)
    return user, old_status

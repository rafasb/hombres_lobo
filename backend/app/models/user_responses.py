"""
Modelos de respuesta específicos para los endpoints de autenticación y usuarios.
Define las estructuras de datos para las respuestas de la API de usuarios.
"""

from pydantic import BaseModel
from typing import List
from app.models.user import User


class LoginResponse(BaseModel):
    """Respuesta para el endpoint de login."""
    success: bool = True
    message: str
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    role: str


class RegisterResponse(BaseModel):
    """Respuesta para el endpoint de registro."""
    success: bool = True
    message: str
    user: User


class UserProfileResponse(BaseModel):
    """Respuesta para obtener perfil de usuario."""
    success: bool = True
    message: str
    user: User


class UsersListResponse(BaseModel):
    """Respuesta para listar usuarios."""
    success: bool = True
    message: str
    users: List[User]
    total_users: int


class UserUpdateResponse(BaseModel):
    """Respuesta para actualización de perfil de usuario."""
    success: bool = True
    message: str
    user: User
    updated_fields: List[str]

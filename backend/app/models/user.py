from pydantic import BaseModel, EmailStr, Field, ConfigDict
from enum import Enum
from datetime import datetime, UTC

# Modelo de usuario (Pydantic)

class UserRole(str, Enum):
    ADMIN = "admin"
    PLAYER = "player"

class UserStatus(str, Enum):
    ACTIVE = "active"   # Estado por defecto del usuario
    BANNED = "banned"   # Usuario bloqueado/baneado
    CONNECTED = "connected" # Usuario conectado a la aplicación
    DISCONNECTED = "disconnected" # Usuario desconectado de la aplicación
    IN_GAME = "in_game" # Usuario en una partida activa

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class User(UserBase):
    id: str
    role: UserRole = UserRole.PLAYER
    status: UserStatus = UserStatus.ACTIVE
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    in_game: bool = False  # Indica si el usuario está en una partida activa
    game_id: str | None = None  # ID de la partida activa, si aplica
    # Otros campos opcionales: fecha de registro, avatar, etc.

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "user_123",
                "username": "loboferoz",
                "email": "loboferoz@email.com",
                "role": "player",
                "status": "active",
                "hashed_password": "$2b$12$EjemploHashSeguro",
                "created_at": "2024-06-01T12:00:00Z",
                "updated_at": "2024-06-01T12:00:00Z",
                "in_game": False,
                "game_id": None
            }
        }
    )

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
    # Puedes añadir más campos editables (avatar, etc.)

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "nuevo@email.com",
                "password": "nueva_contraseña_segura"
            }
        }
    }

class UserStatusUpdate(BaseModel):
    status: UserStatus
    game_id: str | None = None  # ID de la partida activa, si aplica

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "in_game",
                "game_id": "partida_123"
            }
        }
    }

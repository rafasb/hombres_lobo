from pydantic import BaseModel, EmailStr, Field, ConfigDict
from enum import Enum
from datetime import datetime, UTC

# Modelo de usuario (Pydantic)

class UserRole(str, Enum):
    ADMIN = "admin"
    PLAYER = "player"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"

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
    # Otros campos opcionales: fecha de registro, avatar, etc.

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
    # Puedes añadir más campos editables (avatar, etc.)

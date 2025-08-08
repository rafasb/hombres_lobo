"""
Rutas de API para autenticación de usuarios.
Incluye endpoints para registro y login de usuarios.
Estos endpoints no requieren autenticación previa.
"""

from fastapi import APIRouter, HTTPException, Form, status
from app.models.user import User, UserRole, UserStatus
from app.models.user_responses import LoginResponse, UserProfileResponse
from app.services.user_service import create_user, get_all_users
from app.core.security import hash_password, verify_password, create_access_token
import uuid

router = APIRouter()

@router.post("/register", response_model=UserProfileResponse)
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
    
    return UserProfileResponse(
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

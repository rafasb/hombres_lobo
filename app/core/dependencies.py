"""
Dependencias reutilizables para rutas (por ejemplo, obtener usuario actual autenticado).
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import verify_access_token
from app.services.user_service import get_user
from app.models.user import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")
    user_id = payload["sub"]
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
    return user

def admin_required(user=Depends(get_current_user)):
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso solo para administradores")
    return user

def creator_or_admin_required(game_id: str, user=Depends(get_current_user)):
    """Verifica que el usuario sea el creador de la partida o admin."""
    from app.services.game_service import get_game
    
    # Si es admin, tiene acceso total
    if user.role == UserRole.ADMIN:
        return user
    
    # Si no es admin, debe ser el creador de la partida
    game = get_game(game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partida no encontrada")
    
    if game.creator_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el creador o admin pueden realizar esta acción")
    
    return user

def self_or_admin_required(user_id: str, user=Depends(get_current_user)):
    """Verifica que el usuario solo pueda acceder a su propio perfil o sea admin."""
    if user.role == UserRole.ADMIN:
        return user
    
    if user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes acceder a tu propio perfil")
    
    return user

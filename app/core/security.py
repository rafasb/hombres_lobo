"""
Utilidades de autenticación y autorización.
Incluye funciones para hashing y verificación de contraseñas, y generación/validación de tokens JWT.
"""
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

# Contexto de hash para contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración JWT
SECRET_KEY = "supersecretkey"  # Cambiar por una clave segura en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def hash_password(password: str) -> str:
    """Genera un hash seguro para la contraseña."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica que la contraseña en texto plano coincide con el hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Genera un token JWT con los datos proporcionados."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str) -> Optional[dict]:
    """Verifica y decodifica un token JWT. Devuelve los datos si es válido, None si no."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

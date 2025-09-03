import uuid
import pytest

from app.models.user import User, UserStatus, UserAccessRole
from app.database import save_user, load_user, delete_user

def test_save_user_in_game_and_game_id():
    # Crear un usuario de prueba
    user_id = str(uuid.uuid4())
    test_user = User(
        id=user_id,
        username="test_save_user",
        email="test_save_user@example.com",
        hashed_password="test_hashed_pw",
        role=UserAccessRole.PLAYER,
        status=UserStatus.IN_GAME,
        game_id="game_test_123"
    )

    # Asegurar entorno limpio (ignorar errores)
    try:
        delete_user(user_id)
    except Exception:
        pass

    # Guardar usuario
    save_user(test_user)

    # Cargar y comprobar
    loaded = load_user(user_id)
    assert loaded is not None, "El usuario guardado debe poder recuperarse"
    assert loaded.game_id == "game_test_123", "El campo game_id debe persistir correctamente"
    assert loaded.status == UserStatus.IN_GAME, "El estado debe ser IN_GAME"

    # Limpieza
    delete_user(user_id)
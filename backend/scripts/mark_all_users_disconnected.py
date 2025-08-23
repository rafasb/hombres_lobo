"""Script de mantenimiento: marca a todos los usuarios como UserStatus.DISCONNECTED.

Este script usa las funciones públicas del servicio de usuarios para actualizar
el estado de cada usuario y guarda los cambios en la base de datos.
"""
from collections import Counter as _Counter

from app.models.user import UserStatus, UserStatusUpdate
from app.services.user_service import get_all_users, update_user_status

# Fallback directo a la base de datos para estados obsoletos
def fallback_mark_all_disconnected_sqlalchemy():
    """Actualiza directamente la columna `status` de la tabla users a 'disconnected'.

    Este fallback evita la conversión Pydantic/Enum para datos con valores
    obsoletos (por ejemplo, 'active').
    """
    from app.database import get_db_session, UserDB
    from datetime import datetime, UTC

    updated = 0
    with get_db_session() as db:
        users = db.query(UserDB).all()
        for u in users:
            if getattr(u, 'status') != UserStatus.DISCONNECTED.value:
                setattr(u, 'status', UserStatus.DISCONNECTED.value)
                try:
                    setattr(u, 'updated_at', datetime.now(UTC))
                except Exception:
                    pass
                updated += 1
        db.commit()

    print(f"Fallback SQLAlchemy: usuarios actualizados: {updated}")


def main() -> None:
    try:
        users = get_all_users() or []
        print(f"Usuarios detectados: {len(users)}")
    except ValueError as e:
        # Puede ocurrir al convertir enums si hay valores obsoletos en la DB
        print(f"Error cargando usuarios via pydantic: {e}; usando fallback directo.")
        fallback_mark_all_disconnected_sqlalchemy()
        users = get_all_users() or []
        print(f"Usuarios detectados luego del fallback: {len(users)}")

    before = _Counter([u.status for u in users])

    updated = 0
    for u in users:
        # Solo actualizar si no está ya desconectado
        if u.status != UserStatus.DISCONNECTED:
            _, _old = update_user_status(u.id, UserStatusUpdate(status=UserStatus.DISCONNECTED, game_id=None))
            updated += 1

    # Recargar para comprobar
    users_after = get_all_users() or []
    after = _Counter([u.status for u in users_after])

    print("Resumen antes:")
    for k, v in before.items():
        print(f"  {k}: {v}")

    print("Resumen después:")
    for k, v in after.items():
        print(f"  {k}: {v}")

    print(f"Usuarios actualizados: {updated}")


if __name__ == "__main__":
    main()

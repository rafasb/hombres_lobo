#!/usr/bin/env python3
"""Script pequeño para eliminar todas las partidas de la base de datos.

Uso:
  python backend/scripts/delete_all_games.py        # pedirá confirmación
  python backend/scripts/delete_all_games.py --yes # eliminar sin pedir
  python backend/scripts/delete_all_games.py --dry-run # listar sin borrar

Advertencia: Esto eliminará datos de la base de datos SQLite en `backend/db_sqlite/hombres_lobo.db`.
Haz una copia de seguridad si es necesario.
"""
from __future__ import annotations

import argparse
from typing import List

# Importar helpers de la app
from app.database import get_db_session, GameDB


def list_game_ids(session) -> List[str]:
    games = session.query(GameDB).all()
    return [g.id for g in games]


def main() -> int:
    parser = argparse.ArgumentParser(description="Eliminar todas las partidas de la base de datos")
    parser.add_argument("--yes", "-y", action="store_true", help="Confirmar sin pedir interacción")
    parser.add_argument("--dry-run", action="store_true", help="Solo listar las partidas que se eliminarían")
    args = parser.parse_args()

    with get_db_session() as session:
        game_ids = list_game_ids(session)
        if not game_ids:
            print("No hay partidas en la base de datos.")
            return 0

        print(f"Se han encontrado {len(game_ids)} partidas:")
        for gid in game_ids:
            print(f"  - {gid}")

        if args.dry_run:
            print("Dry-run activado: no se realizarán borrados.")
            return 0

        if not args.yes:
            confirm = input("¿Eliminar todas las partidas listadas? (escribe 'yes' para confirmar): ")
            if confirm.strip().lower() != 'yes':
                print("Operación cancelada.")
                return 1

        # Ejecutar borrado en masa
        deleted = session.query(GameDB).delete(synchronize_session=False)
        session.commit()
        print(f"Operación completada: {deleted} partidas eliminadas.")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())

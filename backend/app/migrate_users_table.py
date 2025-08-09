import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'db_sqlite', 'hombres_lobo.db')

def migrate_users_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Añadir columna in_game si no existe
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'in_game' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN in_game BOOLEAN NOT NULL DEFAULT 0")
        print("Columna 'in_game' añadida a 'users'.")
    else:
        print("Columna 'in_game' ya existe.")

    # Añadir columna game_id si no existe
    if 'game_id' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN game_id TEXT NULL")
        print("Columna 'game_id' añadida a 'users'.")
    else:
        print("Columna 'game_id' ya existe.")

    conn.commit()
    conn.close()
    print("Migración completada.")

if __name__ == "__main__":
    migrate_users_table()

"""
Funciones de inicialización y migración de la base de datos
Contiene check_and_migrate_database, initialize_database y funciones de inicio
"""

from sqlalchemy import text

from app.database.session import engine, Base
from app.database.utils import migrate_from_json, create_admin_user
from app.database.models import UserDB


def check_and_migrate_database():
    """Verifica y migra la estructura de la base de datos si es necesario."""
    print("🔄 Verificando estructura de base de datos...")
    
    try:
        with engine.connect() as conn:
            # Verificar si existe la tabla games
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='games'
            """))
            
            if not result.fetchone():
                print("✅ Tabla games no existe, se creará nueva estructura")
                return True
            
            # Verificar columnas existentes en la tabla games
            result = conn.execute(text("PRAGMA table_info(games)"))
            columns = {row[1] for row in result.fetchall()}
            
            required_columns = {
                'id', 'name', 'creator_id', 'max_players', 'player_ids', 
                'players', 'status', 'created_at', 'current_round', 
                'is_first_night', 'night_actions', 'defeated_players',
                'connected_players', 'votes', 'day_votes'
            }
            
            missing_columns = required_columns - columns
            
            if missing_columns:
                print(f"⚠️  Faltan columnas en tabla games: {missing_columns}")
                print("🔄 Migrando estructura de tabla games...")
                
                # Crear tabla temporal con nueva estructura
                conn.execute(text("""
                    CREATE TABLE games_new (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        creator_id TEXT NOT NULL,
                        max_players INTEGER NOT NULL DEFAULT 12,
                        player_ids TEXT NOT NULL DEFAULT '[]',
                        players TEXT NOT NULL DEFAULT '{}',
                        status TEXT NOT NULL DEFAULT 'waiting',
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        current_round INTEGER NOT NULL DEFAULT 0,
                        is_first_night BOOLEAN NOT NULL DEFAULT 1,
                        night_actions TEXT NOT NULL DEFAULT '{}',
                        defeated_players TEXT NOT NULL DEFAULT '[]',
                        connected_players TEXT NOT NULL DEFAULT '[]',
                        votes TEXT NOT NULL DEFAULT '{}',
                        day_votes TEXT NOT NULL DEFAULT '{}'
                    )
                """))
                
                # Migrar datos existentes (solo columnas que coincidan)
                existing_columns = columns.intersection(required_columns)
                if existing_columns:
                    columns_str = ', '.join(existing_columns)
                    conn.execute(text(f"""
                        INSERT INTO games_new ({columns_str})
                        SELECT {columns_str} FROM games
                    """))
                
                # Reemplazar tabla antigua
                conn.execute(text("DROP TABLE games"))
                conn.execute(text("ALTER TABLE games_new RENAME TO games"))
                
                # Crear índices
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_games_creator_id ON games (creator_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_games_status ON games (status)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_games_created_at ON games (created_at)"))
                
                conn.commit()
                print("✅ Migración de tabla games completada")
            else:
                print("✅ Estructura de tabla games correcta")
                
    except Exception as e:
        print(f"❌ Error durante migración: {e}")
        raise
    
    return True


def initialize_database():
    """Inicializa la base de datos con verificación y migración."""
    print("🔄 Inicializando base de datos...")
    
    # Verificar y migrar si es necesario
    check_and_migrate_database()
    
    # Crear estructura completa
    Base.metadata.create_all(bind=engine)
    
    print("✅ Base de datos inicializada correctamente")


def auto_initialize():
    """Ejecuta la inicialización automática al cargar el módulo."""
    try:
        initialize_database()
        
        # Intentar migración desde JSON si la base de datos está vacía
        from app.database.utils import get_db_session
        with get_db_session() as db:
            user_count = db.query(UserDB).count()
            if user_count == 0:
                print("📦 Base de datos vacía, ejecutando migración desde JSON...")
                migrate_from_json()
        
        # Crear usuario admin por defecto
        create_admin_user()
        
    except Exception as e:
        print(f"⚠️  Error durante la inicialización automática: {e}")
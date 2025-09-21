"""
Módulo database refactorizado
Mantiene compatibilidad con el módulo database.py original
"""

# Importar configuración de sesión
from .session import (
    engine, SessionLocal, Base, DATABASE_URL,
    get_db_session, get_db
)

# Importar modelos SQLAlchemy
from .models import UserDB, GameDB

# Importar funciones de conversión (se aplican automáticamente a los modelos)
from .conversions import UserDBConversions, GameDBConversions

# Importar funciones de utilidades y CRUD
from .utils import (
    # Funciones de migración
    migrate_from_json, create_admin_user,
    
    # Funciones para usuarios
    save_user, load_user, load_all_users, delete_user,
    find_user_by_username, find_user_by_email,
    
    # Funciones para partidas
    save_game, load_game, load_all_games, delete_game,
    find_games_by_creator, find_games_by_status, find_games_by_player_id,
    
    # Funciones helper
    get_game_players, get_game_player_by_id, get_game_with_players,
    game_to_response
)

# Importar funciones de inicialización
from .initialization import (
    check_and_migrate_database, initialize_database, auto_initialize
)

# Ejecutar inicialización automática al importar el módulo
auto_initialize()

# Exportar todo para compatibilidad
__all__ = [
    # Configuración
    'engine', 'SessionLocal', 'Base', 'DATABASE_URL',
    'get_db_session', 'get_db',
    
    # Modelos
    'UserDB', 'GameDB',
    
    # Conversiones
    'UserDBConversions', 'GameDBConversions',
    
    # Utilidades - Usuarios
    'save_user', 'load_user', 'load_all_users', 'delete_user',
    'find_user_by_username', 'find_user_by_email',
    
    # Utilidades - Partidas
    'save_game', 'load_game', 'load_all_games', 'delete_game',
    'find_games_by_creator', 'find_games_by_status', 'find_games_by_player_id',
    
    # Helpers
    'get_game_players', 'get_game_player_by_id', 'get_game_with_players',
    'game_to_response',
    
    # Inicialización
    'check_and_migrate_database', 'initialize_database', 'migrate_from_json',
    'create_admin_user'
]
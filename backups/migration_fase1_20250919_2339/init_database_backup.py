#!/usr/bin/env python3
"""
Script de inicialización de la base de datos SQLite
Migra datos desde JSON, verifica integridad y optimiza el rendimiento.
"""

import os
import sys
import json
import shutil
from datetime import datetime, UTC
from pathlib import Path

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import (
    engine, Base, SessionLocal, UserDB, GameDB,
    get_db_session, initialize_database
)
from app.models.user import UserAccessRole, UserStatus
from app.models.game_and_player import GameStatus
from app.core.security import hash_password
from sqlalchemy import text, Index
import uuid

def create_backup():
    """Crea backup de los datos JSON antes de la migración."""
    print("🔄 Creando backup de datos JSON...")
    
    json_dir = Path(__file__).parent / 'app' / 'db_json'
    backup_dir = Path(__file__).parent / 'backups' / f"json_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if json_dir.exists():
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        for json_file in json_dir.glob('*.json'):
            shutil.copy2(json_file, backup_dir / json_file.name)
        
        print(f"✅ Backup creado en: {backup_dir}")
        return backup_dir
    else:
        print("⚠️  No se encontraron datos JSON para respaldar")
        return None

def validate_env_credentials():
    """Valida que las credenciales del .env sean válidas."""
    print("🔄 Validando credenciales de entorno...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    admin_username = os.getenv('ADMIN_USERNAME')
    admin_email = os.getenv('ADMIN_EMAIL')
    admin_password = os.getenv('ADMIN_PASSWORD')
    
    if not all([admin_username, admin_email, admin_password]):
        print("❌ Credenciales de admin incompletas en .env")
        return False
    
    if not admin_password or len(admin_password) < 6:
        print("❌ La contraseña del admin debe tener al menos 6 caracteres")
        return False
    
    print("✅ Credenciales de entorno validadas")
    return True

def create_initial_users():
    """Crea solo los usuarios iniciales definidos en el .env."""
    print("🔄 Creando usuarios iniciales...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    # Credenciales del admin
    admin_username = os.getenv('ADMIN_USERNAME')
    admin_email = os.getenv('ADMIN_EMAIL')
    admin_password = os.getenv('ADMIN_PASSWORD')
    
    # Credenciales del usuario de prueba
    user_username = os.getenv('USERNAME')
    user_email = os.getenv('EMAIL')
    user_password = os.getenv('PASSWORD')
    
    with get_db_session() as db:
        # Verificar usuarios existentes
        existing_admin = db.query(UserDB).filter(UserDB.username == admin_username).first()
        existing_user = db.query(UserDB).filter(UserDB.username == user_username).first() if user_username else None
        
        users_created = 0
        
        # Crear usuario admin si no existe
        if admin_username and admin_email and admin_password and not existing_admin:
            admin_user = UserDB(
                id=str(uuid.uuid4()),
                username=admin_username,
                email=admin_email,
                hashed_password=hash_password(admin_password),
                role=UserAccessRole.ADMIN.value,
                status=UserStatus.DISCONNECTED.value,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
            db.add(admin_user)
            users_created += 1
            print(f"✅ Usuario admin creado: {admin_username} ({admin_email})")
        elif existing_admin:
            print(f"ℹ️  Usuario admin ya existe: {admin_username}")
        
        # Crear usuario de prueba si no existe
        if user_username and user_email and user_password and not existing_user:
            test_user = UserDB(
                id=str(uuid.uuid4()),
                username=user_username,
                email=user_email,
                hashed_password=hash_password(user_password),
                role=UserAccessRole.PLAYER.value,
                status=UserStatus.DISCONNECTED.value,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
            db.add(test_user)
            users_created += 1
            print(f"✅ Usuario de prueba creado: {user_username} ({user_email})")
        elif existing_user:
            print(f"ℹ️  Usuario de prueba ya existe: {user_username}")
        
        if users_created > 0:
            db.commit()
            print(f"💾 {users_created} usuarios guardados en la base de datos")

def optimize_database():
    """Optimiza la base de datos creando índices adicionales."""
    print("🔄 Optimizando base de datos...")
    
    try:
        with engine.connect() as conn:
            # Índices adicionales para optimización
            optimization_indices = [
                "CREATE INDEX IF NOT EXISTS idx_users_username ON users (username)",
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)",
                "CREATE INDEX IF NOT EXISTS idx_users_role ON users (role)",
                "CREATE INDEX IF NOT EXISTS idx_users_status ON users (status)",
                "CREATE INDEX IF NOT EXISTS idx_users_game_id ON users (game_id)",
                "CREATE INDEX IF NOT EXISTS idx_users_created_at ON users (created_at)",
                
                "CREATE INDEX IF NOT EXISTS idx_games_creator_id ON games (creator_id)",
                "CREATE INDEX IF NOT EXISTS idx_games_status ON games (status)",
                "CREATE INDEX IF NOT EXISTS idx_games_created_at ON games (created_at)",
                "CREATE INDEX IF NOT EXISTS idx_games_current_round ON games (current_round)"
            ]
            
            for index_sql in optimization_indices:
                try:
                    conn.execute(text(index_sql))
                except Exception as idx_error:
                    print(f"⚠️  Índice ya existe o error: {idx_error}")
            
            # Optimización SQLite
            conn.execute(text("ANALYZE"))
            conn.execute(text("VACUUM"))
            
            conn.commit()
            print("✅ Optimización completada")
            
    except Exception as e:
        print(f"⚠️  Error durante optimización: {e}")

def create_database_info():
    """Crea archivo de información sobre la base de datos."""
    print("🔄 Creando información de la base de datos...")
    
    with get_db_session() as db:
        user_count = db.query(UserDB).count()
        game_count = db.query(GameDB).count()
        
        # Estadísticas por rol
        admin_count = db.query(UserDB).filter(UserDB.role == UserAccessRole.ADMIN.value).count()
        player_count = db.query(UserDB).filter(UserDB.role == UserAccessRole.PLAYER.value).count()
        
        # Estadísticas por estado
        banned_users = db.query(UserDB).filter(UserDB.status == UserStatus.BANNED.value).count()
        
        # Estadísticas de partidas
        waiting_games = db.query(GameDB).filter(GameDB.status == GameStatus.WAITING.value).count()
        playing_games = db.query(GameDB).filter(GameDB.status.in_([
            GameStatus.STARTED.value, 
            GameStatus.NIGHT.value, 
            GameStatus.DAY.value,
            GameStatus.VOTING.value
        ])).count()
        finished_games = db.query(GameDB).filter(GameDB.status == GameStatus.FINISHED.value).count()
        
        db_info = {
            "database_initialized": datetime.now(UTC).isoformat(),
            "statistics": {
                "users": {
                    "total": user_count,
                    "admins": admin_count,
                    "players": player_count,
                    "banned": banned_users
                },
                "games": {
                    "total": game_count,
                    "waiting": waiting_games,
                    "playing": playing_games,
                    "finished": finished_games
                }
            }
        }
    
    info_file = Path(__file__).parent / 'app' / 'db_sqlite' / 'db_info.json'
    info_file.parent.mkdir(exist_ok=True)
    
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(db_info, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Información de BD guardada en: {info_file}")
    
    # Mostrar resumen
    print("\n📊 RESUMEN DE LA BASE DE DATOS:")
    print(f"   👥 Usuarios: {user_count} (👑 {admin_count} admins, 👤 {player_count} jugadores)")
    print(f"   🎮 Partidas: {game_count} (⏳ {waiting_games} esperando, ▶️ {playing_games} jugando, ✅ {finished_games} terminadas)")

def verify_database_integrity():
    """Verifica la integridad de la base de datos."""
    print("🔄 Verificando integridad de la base de datos...")
    
    try:
        with get_db_session() as db:
            # Verificar que se pueden cargar usuarios
            users = db.query(UserDB).limit(5).all()
            if users:
                print(f"✅ Usuarios cargados correctamente (muestra: {len(users)})")
                
                # Verificar conversión Pydantic
                for user in users[:2]:  # Solo los primeros 2 para prueba
                    pydantic_user = user.to_pydantic()
                    print(f"   - Usuario: {pydantic_user.username} ({pydantic_user.role.value})")
            
            # Verificar que se pueden cargar partidas
            games = db.query(GameDB).limit(5).all()
            if games:
                print(f"✅ Partidas cargadas correctamente (muestra: {len(games)})")
                
                # Verificar conversión Pydantic
                for game in games[:2]:  # Solo las primeras 2 para prueba
                    pydantic_game = game.to_pydantic()
                    print(f"   - Partida: {pydantic_game.name} ({pydantic_game.status.value})")
            else:
                print("ℹ️  No hay partidas en la base de datos")
                
    except Exception as e:
        print(f"❌ Error verificando integridad: {e}")
        raise

def main():
    """Función principal del script de inicialización."""
    print("🚀 INICIANDO CONFIGURACIÓN DE BASE DE DATOS HOMBRES LOBO")
    print("=" * 60)
    
    try:
        # 1. Validar credenciales
        if not validate_env_credentials():
            return False
        
        # 2. Crear backup
        backup_dir = create_backup()
        
        # 3. Inicializar estructura de BD (incluye migración automática)
        initialize_database()
        
        # 4. Crear usuarios iniciales
        create_initial_users()
        
        # 5. Optimizar base de datos
        optimize_database()
        
        # 6. Verificar integridad
        verify_database_integrity()
        
        # 7. Crear información de BD
        create_database_info()
        
        print("\n" + "=" * 60)
        print("🎉 INICIALIZACIÓN COMPLETADA EXITOSAMENTE")
        print("\n📝 Próximos pasos:")
        print("   1. Ejecutar: uvicorn app.main:app --reload")
        print("   2. Acceder a: http://localhost:8000/docs")
        print("   3. Hacer login con las credenciales del .env")
        
        if backup_dir:
            print(f"\n💾 Backup disponible en: {backup_dir}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LA INICIALIZACIÓN: {e}")
        print("\n🔍 Para debug, revisa:")
        print("   - Permisos de archivos")
        print("   - Configuración del .env")
        print("   - Logs de la aplicación")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
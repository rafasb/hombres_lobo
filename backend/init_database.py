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
    get_db_session
)
from app.models.user import UserRole, UserStatus
from app.models.game_and_roles import GameStatus
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

def create_database_structure():
    """Crea la estructura de la base de datos."""
    print("🔄 Creando estructura de base de datos...")
    
    try:
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas correctamente")
        
        # Crear índices adicionales para optimización
        with engine.connect() as conn:
            # Índices para búsquedas frecuentes
            try:
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_username ON users (username)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_role ON users (role)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_status ON users (status)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_created_at ON users (created_at)"))
                
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_games_creator_id ON games (creator_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_games_status ON games (status)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_games_created_at ON games (created_at)"))
                
                conn.commit()
                print("✅ Índices de optimización creados")
                
            except Exception as e:
                print(f"⚠️  Algunos índices ya existían: {e}")
                
    except Exception as e:
        print(f"❌ Error creando estructura de base de datos: {e}")
        raise

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
        # Limpiar usuarios existentes
        existing_users = db.query(UserDB).all()
        for user in existing_users:
            db.delete(user)
        db.commit()
        print("🗑️  Usuarios existentes eliminados")
        
        # Crear usuario admin
        if admin_username and admin_email and admin_password:
            admin_user = UserDB(
                id=str(uuid.uuid4()),
                username=admin_username,
                email=admin_email,
                hashed_password=hash_password(admin_password),
                role=UserRole.ADMIN.value,
                status=UserStatus.ACTIVE.value,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
            db.add(admin_user)
            print(f"✅ Usuario admin creado: {admin_username} ({admin_email})")
        
        # Crear usuario de prueba
        if user_username and user_email and user_password:
            test_user = UserDB(
                id=str(uuid.uuid4()),
                username=user_username,
                email=user_email,
                hashed_password=hash_password(user_password),
                role=UserRole.PLAYER.value,
                status=UserStatus.ACTIVE.value,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
            db.add(test_user)
            print(f"✅ Usuario de prueba creado: {user_username} ({user_email})")
        
        db.commit()

def cleanup_existing_admin_users():
    """Elimina usuarios administradores existentes (solo si se va a recrear admin)."""
    # Esta función ya no es necesaria en el flujo normal
    pass


def create_database_info():
    """Crea archivo de información sobre la base de datos."""
    print("🔄 Creando información de la base de datos...")
    
    with get_db_session() as db:
        user_count = db.query(UserDB).count()
        game_count = db.query(GameDB).count()
        
        # Estadísticas por rol
        admin_count = db.query(UserDB).filter(UserDB.role == UserRole.ADMIN.value).count()
        player_count = db.query(UserDB).filter(UserDB.role == UserRole.PLAYER.value).count()
        
        # Estadísticas por estado
        active_users = db.query(UserDB).filter(UserDB.status == UserStatus.ACTIVE.value).count()
        
        # Estadísticas de partidas
        waiting_games = db.query(GameDB).filter(GameDB.status == GameStatus.WAITING.value).count()
        playing_games = db.query(GameDB).filter(GameDB.status == GameStatus.STARTED.value).count()
        finished_games = db.query(GameDB).filter(GameDB.status == GameStatus.FINISHED.value).count()
        
        db_info = {
            "database_initialized": datetime.now(UTC).isoformat(),
            "statistics": {
                "users": {
                    "total": user_count,
                    "admins": admin_count,
                    "players": player_count,
                    "active": active_users
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
        
        # 3. Crear estructura de BD
        create_database_structure()
        
        # 6. Crear información de BD
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
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

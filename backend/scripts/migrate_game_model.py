#!/usr/bin/env python3
"""
Script de Migración FASE 2 - Añadir nuevos campos a tabla games
Actualiza la base de datos existente sin perder información.
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text, inspect
from contextlib import contextmanager

# Añadir el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import DATABASE_URL, SessionLocal, GameDB, Base

def check_database_integrity():
    """Verifica que la base de datos esté en estado consistente."""
    print("🔍 Verificando integridad de la base de datos...")
    
    try:
        with SessionLocal() as db:
            # Verificar que la tabla games existe
            result = db.execute(text("SELECT COUNT(*) FROM games")).scalar()
            print(f"✅ Tabla 'games' existe con {result} registros")
            return True
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        return False

def backup_current_data():
    """Crea backup de los datos actuales antes de migrar."""
    backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"migration_backup_{backup_timestamp}"
    
    print(f"📦 Creando backup en: {backup_dir}")
    
    try:
        os.makedirs(backup_dir, exist_ok=True)
        
        # Copiar archivo de base de datos completo
        db_file = DATABASE_URL.replace("sqlite:///", "")
        backup_db_file = os.path.join(backup_dir, "hombres_lobo_pre_migration.db")
        
        import shutil
        shutil.copy2(db_file, backup_db_file)
        
        print(f"✅ Backup creado: {backup_db_file}")
        return backup_dir
    except Exception as e:
        print(f"❌ Error creando backup: {e}")
        return None

def check_new_columns_exist():
    """Verifica si las nuevas columnas ya existen."""
    print("🔍 Verificando si las nuevas columnas ya existen...")
    
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('games')]
        
        new_columns = [
            'current_phase', 'phase_start_time', 'phase_duration_seconds', 
            'phase_auto_advance', 'next_phase_at', 'phase_end_actions',
            'voting_active', 'voting_start_time', 'voting_end_time', 'voting_type',
            'pending_night_actions', 'completed_night_actions', 'night_action_deadline',
            'auto_advance_enabled', 'manual_control', 'game_speed',
            'last_game_activity', 'inactive_players'
        ]
        
        existing_new_columns = [col for col in new_columns if col in columns]
        missing_columns = [col for col in new_columns if col not in columns]
        
        if existing_new_columns:
            print(f"⚠️  Algunas columnas ya existen: {existing_new_columns}")
        
        if missing_columns:
            print(f"🆕 Columnas por añadir: {missing_columns}")
            return False, missing_columns
        else:
            print("✅ Todas las nuevas columnas ya existen")
            return True, []
            
    except Exception as e:
        print(f"❌ Error verificando columnas: {e}")
        return False, []

def add_new_columns():
    """Añade las nuevas columnas a la tabla games."""
    print("🔧 Añadiendo nuevas columnas a la tabla games...")
    
    # SQL para añadir cada nueva columna
    column_definitions = [
        # Gestión de Fases
        "ALTER TABLE games ADD COLUMN current_phase TEXT NOT NULL DEFAULT 'waiting'",
        "ALTER TABLE games ADD COLUMN phase_start_time DATETIME",
        "ALTER TABLE games ADD COLUMN phase_duration_seconds INTEGER",
        "ALTER TABLE games ADD COLUMN phase_auto_advance BOOLEAN NOT NULL DEFAULT 1",
        
        # Temporizadores Persistentes
        "ALTER TABLE games ADD COLUMN next_phase_at DATETIME",
        "ALTER TABLE games ADD COLUMN phase_end_actions TEXT NOT NULL DEFAULT '[]'",
        
        # Estado de Votación
        "ALTER TABLE games ADD COLUMN voting_active BOOLEAN NOT NULL DEFAULT 0",
        "ALTER TABLE games ADD COLUMN voting_start_time DATETIME",
        "ALTER TABLE games ADD COLUMN voting_end_time DATETIME",
        "ALTER TABLE games ADD COLUMN voting_type TEXT",
        
        # Acciones Nocturnas Ampliadas
        "ALTER TABLE games ADD COLUMN pending_night_actions TEXT NOT NULL DEFAULT '{}'",
        "ALTER TABLE games ADD COLUMN completed_night_actions TEXT NOT NULL DEFAULT '[]'",
        "ALTER TABLE games ADD COLUMN night_action_deadline DATETIME",
        
        # Metadata de Juego
        "ALTER TABLE games ADD COLUMN auto_advance_enabled BOOLEAN NOT NULL DEFAULT 1",
        "ALTER TABLE games ADD COLUMN manual_control BOOLEAN NOT NULL DEFAULT 0",
        "ALTER TABLE games ADD COLUMN game_speed TEXT NOT NULL DEFAULT 'normal'",
        
        # Estado de Actividad de Jugadores
        "ALTER TABLE games ADD COLUMN last_game_activity TEXT NOT NULL DEFAULT '{}'",
        "ALTER TABLE games ADD COLUMN inactive_players TEXT NOT NULL DEFAULT '[]'"
    ]
    
    try:
        engine = create_engine(DATABASE_URL)
        with engine.begin() as conn:
            for sql in column_definitions:
                try:
                    conn.execute(text(sql))
                    column_name = sql.split("ADD COLUMN ")[1].split(" ")[0]
                    print(f"  ✅ Añadida columna: {column_name}")
                except Exception as e:
                    # Si la columna ya existe, continuar
                    if "duplicate column name" in str(e).lower():
                        column_name = sql.split("ADD COLUMN ")[1].split(" ")[0]
                        print(f"  ⚠️  Columna ya existe: {column_name}")
                    else:
                        raise e
        
        print("✅ Todas las columnas añadidas exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error añadiendo columnas: {e}")
        return False

def migrate_existing_data():
    """Migra datos existentes estableciendo valores por defecto inteligentes."""
    print("🔄 Migrando datos existentes...")
    
    try:
        with SessionLocal() as db:
            # Obtener todos los juegos existentes
            games = db.execute(text("SELECT id, status, created_at FROM games")).fetchall()
            
            for game in games:
                game_id, status, created_at = game
                
                # Mapear status actual a current_phase
                status_to_phase = {
                    "waiting": "waiting",
                    "started": "day_discussion", 
                    "night": "night_actions",
                    "day": "day_discussion",
                    "paused": "paused",
                    "finished": "game_over"
                }
                
                current_phase = status_to_phase.get(status, "waiting")
                phase_start_time = created_at or datetime.utcnow()
                
                # Actualizar el juego con valores inteligentes
                update_sql = text("""
                    UPDATE games 
                    SET current_phase = :current_phase,
                        phase_start_time = :phase_start_time
                    WHERE id = :game_id AND 
                          (current_phase = 'waiting' OR current_phase IS NULL)
                """)
                
                db.execute(update_sql, {
                    "current_phase": current_phase,
                    "phase_start_time": phase_start_time,
                    "game_id": game_id
                })
                
                print(f"  ✅ Migrado juego {game_id}: {status} -> {current_phase}")
            
            db.commit()
            print(f"✅ Migrados {len(games)} juegos exitosamente")
            return True
            
    except Exception as e:
        print(f"❌ Error migrando datos: {e}")
        return False

def verify_migration():
    """Verifica que la migración se completó correctamente."""
    print("🔍 Verificando migración...")
    
    try:
        with SessionLocal() as db:
            # Verificar que las nuevas columnas tienen datos
            result = db.execute(text("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN current_phase IS NOT NULL THEN 1 ELSE 0 END) as with_phase,
                       SUM(CASE WHEN phase_start_time IS NOT NULL THEN 1 ELSE 0 END) as with_start_time
                FROM games
            """)).fetchone()
            
            total, with_phase, with_start_time = result
            
            print(f"📊 Estadísticas de migración:")
            print(f"   Total juegos: {total}")
            print(f"   Con current_phase: {with_phase}")
            print(f"   Con phase_start_time: {with_start_time}")
            
            if total > 0 and with_phase == total:
                print("✅ Migración verificada exitosamente")
                return True
            else:
                print("⚠️  Migración incompleta")
                return False
                
    except Exception as e:
        print(f"❌ Error verificando migración: {e}")
        return False

def main():
    """Función principal del script de migración."""
    print("🚀 INICIANDO MIGRACIÓN FASE 2: Nuevos campos Game")
    print("=" * 50)
    
    # 1. Verificar integridad inicial
    if not check_database_integrity():
        print("❌ ABORTANDO: Base de datos no está en estado consistente")
        return False
    
    # 2. Crear backup
    backup_dir = backup_current_data()
    if not backup_dir:
        print("❌ ABORTANDO: No se pudo crear backup")
        return False
    
    # 3. Verificar si la migración ya se ejecutó
    already_migrated, missing_columns = check_new_columns_exist()
    if already_migrated:
        print("✅ MIGRACIÓN YA COMPLETADA: Todas las columnas existen")
        return True
    
    # 4. Añadir nuevas columnas
    if not add_new_columns():
        print(f"❌ ABORTANDO: Error añadiendo columnas")
        print(f"💾 Restaurar desde backup: {backup_dir}")
        return False
    
    # 5. Migrar datos existentes
    if not migrate_existing_data():
        print(f"❌ ABORTANDO: Error migrando datos")
        print(f"💾 Restaurar desde backup: {backup_dir}")
        return False
    
    # 6. Verificar migración
    if not verify_migration():
        print(f"⚠️  ADVERTENCIA: Migración puede estar incompleta")
        print(f"💾 Backup disponible en: {backup_dir}")
        return False
    
    print("=" * 50)
    print("🎉 MIGRACIÓN FASE 2 COMPLETADA EXITOSAMENTE")
    print(f"💾 Backup guardado en: {backup_dir}")
    print("🎯 La base de datos está lista para usar nuevos campos")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
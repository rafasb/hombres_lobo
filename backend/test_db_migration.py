#!/usr/bin/env python3
"""
Script de prueba para verificar la migración de base de datos
con los nuevos campos del modelo Game
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.database import get_db_session, GameDB
from app.models.game_and_player import Game, GameStatus, PlayerInfo, Roles
from datetime import datetime, UTC

def test_database_migration():
    """Prueba la migración de base de datos con los nuevos campos"""
    print("🧪 Iniciando prueba de migración de base de datos...")
    
    try:
        # Crear un juego de prueba con los nuevos campos
        test_game = Game(
            id="test-game-001",
            name="Juego de Prueba Migración",
            creator_id="user-123",
            max_players=10,
            player_ids=["user-123", "user-456", "user-789"],
            players={
                "user-123": PlayerInfo(player_id="user-123", role=Roles.VILLAGER, is_alive=True),
                "user-456": PlayerInfo(player_id="user-456", role=Roles.SEER, is_alive=True),
                "user-789": PlayerInfo(player_id="user-789", role=Roles.WAREWOLF, is_alive=False)
            },
            status=GameStatus.DAY,
            created_at=datetime.now(UTC),
            current_round=2,
            is_first_night=False,
            night_actions={"user-456": {"action": "seer", "target": "user-789"}},
            # Nuevos campos
            eliminated_players=["user-789"],
            connected_players=["user-123", "user-456"],
            votes={"user-123": "user-789", "user-456": "user-789"}
        )
        
        print("✅ Juego de prueba creado exitosamente")
        
        # Guardar en base de datos
        with get_db_session() as db:
            # Eliminar juego de prueba previo si existe
            existing = db.query(GameDB).filter(GameDB.id == "test-game-001").first()
            if existing:
                db.delete(existing)
                db.commit()
            
            # Crear nuevo registro
            db_game = GameDB.from_pydantic(test_game)
            db.add(db_game)
            db.commit()
            
            print("✅ Juego guardado en base de datos")
            
            # Leer desde base de datos
            retrieved_db_game = db.query(GameDB).filter(GameDB.id == "test-game-001").first()
            if not retrieved_db_game:
                print("❌ No se pudo recuperar el juego desde la base de datos")
                return False
                
            # Convertir de vuelta a modelo Pydantic
            retrieved_game = retrieved_db_game.to_pydantic()
            
            print("✅ Juego recuperado desde base de datos")
            
            # Verificar que los nuevos campos se guardaron y cargaron correctamente
            print("🔍 Verificando integridad de datos:")
            
            assert retrieved_game.id == test_game.id
            print("  ✅ ID correcto")
            
            assert retrieved_game.eliminated_players == test_game.eliminated_players
            print("  ✅ eliminated_players correcto:", retrieved_game.eliminated_players)
            
            assert retrieved_game.connected_players == test_game.connected_players
            print("  ✅ connected_players correcto:", retrieved_game.connected_players)
            
            assert retrieved_game.votes == test_game.votes
            print("  ✅ votes correcto:", retrieved_game.votes)
            
            # Verificar compatibilidad con day_votes
            assert retrieved_game.day_votes == retrieved_game.votes
            print("  ✅ Compatibilidad day_votes correcta")
            
            # Verificar que los métodos nuevos funcionan
            living_players = retrieved_game.get_living_players()
            assert "user-789" not in living_players
            print("  ✅ get_living_players correcto:", living_players)
            
            vote_count = retrieved_game.get_vote_count()
            assert vote_count["user-789"] == 2
            print("  ✅ get_vote_count correcto:", vote_count)
            
            most_voted = retrieved_game.get_most_voted()
            assert most_voted == "user-789"
            print("  ✅ get_most_voted correcto:", most_voted)
            
            # Limpiar
            db.delete(retrieved_db_game)
            db.commit()
            print("🧹 Juego de prueba eliminado")
            
        print("🎉 ¡Prueba de migración completada exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database_migration()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Script de prueba para verificar que la refactorización de GameState
funciona correctamente como wrapper de servicios
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import asyncio
from app.models.game_and_player import Game, GameStatus, PlayerInfo, Roles
from app.services.game_state_service import GameState
from datetime import datetime, UTC

async def test_game_state_refactoring():
    """Prueba la refactorización de GameState como wrapper de servicios"""
    print("🧪 Iniciando prueba de refactorización GameState...")
    
    try:
        # Crear un juego de prueba
        test_game = Game(
            id="test-refactor-001",
            name="Juego Refactorización Test",
            creator_id="user-creator",
            max_players=8,
            player_ids=["user-creator", "user-2", "user-3", "user-4"],
            players={
                "user-creator": PlayerInfo(player_id="user-creator", role=Roles.VILLAGER, is_alive=True),
                "user-2": PlayerInfo(player_id="user-2", role=Roles.SEER, is_alive=True),
                "user-3": PlayerInfo(player_id="user-3", role=Roles.WAREWOLF, is_alive=True),
                "user-4": PlayerInfo(player_id="user-4", role=Roles.HUNTER, is_alive=False)  # Muerto
            },
            status=GameStatus.DAY,
            created_at=datetime.now(UTC),
            current_round=2,
            is_first_night=False,
            night_actions={"user-2": {"action": "seer", "target": "user-3"}},
            eliminated_players=["user-4"],
            connected_players=["user-creator", "user-2", "user-3"],
            votes={}
        )
        
        print("✅ Juego de prueba creado")
        
        # Crear GameState wrapper
        game_state = GameState("test-refactor-001", test_game)
        
        print("✅ GameState wrapper creado")
        
        # Verificar que las propiedades deleguen correctamente
        print("🔍 Verificando propiedades delegadas:")
        
        assert len(game_state.players) == 4
        print(f"  ✅ players: {len(game_state.players)} jugadores")
        
        assert len(game_state.player_ids) == 4
        print(f"  ✅ player_ids: {game_state.player_ids}")
        
        assert len(game_state.connected_players) == 3
        print(f"  ✅ connected_players: {game_state.connected_players}")
        
        assert len(game_state.eliminated_players) == 1
        print(f"  ✅ eliminated_players: {game_state.eliminated_players}")
        
        assert game_state.is_first_night == False
        print(f"  ✅ is_first_night: {game_state.is_first_night}")
        
        # Verificar métodos delegados
        print("🔍 Verificando métodos delegados:")
        
        living_players = game_state.get_living_players()
        assert len(living_players) == 3
        assert "user-4" not in living_players
        print(f"  ✅ get_living_players: {living_players}")
        
        dead_players = game_state.get_dead_players()
        assert len(dead_players) == 1
        assert "user-4" in dead_players
        print(f"  ✅ get_dead_players: {dead_players}")
        
        # Probar votación
        vote_result = game_state.cast_vote("user-creator", "user-3")
        assert vote_result == True
        print(f"  ✅ cast_vote exitoso")
        
        vote_count = game_state.get_vote_count()
        assert vote_count["user-3"] == 1
        print(f"  ✅ get_vote_count: {vote_count}")
        
        most_voted = game_state.get_most_voted()
        assert most_voted == "user-3"
        print(f"  ✅ get_most_voted: {most_voted}")
        
        # Probar eliminación de jugador
        game_state.eliminate_player("user-2")
        
        updated_living = game_state.get_living_players()
        assert len(updated_living) == 2
        assert "user-2" not in updated_living
        print(f"  ✅ eliminate_player funcionando: jugadores vivos = {updated_living}")
        
        # Probar gestión de jugadores conectados
        game_state.add_connected_player("user-5")
        assert "user-5" in game_state.connected_players
        print(f"  ✅ add_connected_player: {game_state.connected_players}")
        
        game_state.remove_connected_player("user-5")
        assert "user-5" not in game_state.connected_players
        print(f"  ✅ remove_connected_player: {game_state.connected_players}")
        
        # Probar acciones nocturnas
        game_state.set_night_action("user-3", {"action": "werewolf_kill", "target": "user-creator"})
        assert "user-3" in game_state.night_actions
        print(f"  ✅ set_night_action: {game_state.night_actions}")
        
        game_state.clear_night_actions()
        assert len(game_state.night_actions) == 0
        print(f"  ✅ clear_night_actions: acciones limpiadas")
        
        # Verificar que los cambios se reflejan en game_data
        print("🔍 Verificando sincronización con game_data:")
        
        assert len(game_state.game_data.eliminated_players) == 2  # user-4 y user-2
        print(f"  ✅ game_data.eliminated_players actualizado: {game_state.game_data.eliminated_players}")
        
        assert len(game_state.game_data.votes) == 1
        print(f"  ✅ game_data.votes actualizado: {game_state.game_data.votes}")
        
        # Limpiar votos
        game_state.clear_votes()
        assert len(game_state.votes) == 0
        print(f"  ✅ clear_votes funcionando")
        
        print("🎉 ¡Prueba de refactorización completada exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_game_state_refactoring())
    sys.exit(0 if success else 1)

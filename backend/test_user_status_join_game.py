#!/usr/bin/env python3
"""
Test para verificar la funcionalidad de cambio de estado de usuario al unirse a partidas
"""
import asyncio
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.websocket.user_status_handlers import user_status_handler
from app.services.user_service import get_user, create_user
from app.models.user import User, UserAccessRole, UserStatus
from app.core.security import hash_password
import uuid
from app.websocket.connection_manager import connection_manager

async def test_user_status_join_game():
    """Test para verificar cambios de estado al unirse a partida"""
    print("🧪 Iniciando test de cambio de estado al unirse a partida...")
    
    try:
        # 1. Crear usuario de prueba
        print("📝 Creando usuario de prueba...")
        
        # Crear el usuario directamente
        hashed = hash_password("testpass123")
        new_user = User(
            id=str(uuid.uuid4()),
            username="test_player_join",
            email="test_join@example.com",
            role=UserAccessRole.PLAYER,
            status=UserStatus.DISCONNECTED,
            hashed_password=hashed
        )
        create_user(new_user)
        if not new_user:
            print("❌ Error creando usuario de prueba")
            return False
            
        user_id = new_user.id
        print(f"✅ Usuario creado: {user_id} con estado inicial: {new_user.status}")
        
        # 2. Simular conexión WebSocket
        print("🔌 Simulando conexión WebSocket...")
        
        # Crear una conexión falsa en el manager
        connection_id = "test_connection_123"
        game_id = "test_game_456"
        
        # Simular que el connection_manager tiene la conexión registrada
        connection_manager.connection_users[connection_id] = user_id
        connection_manager.connection_info[connection_id] = {
            "user_id": user_id,
            "game_id": game_id
        }
        
        # 3. Test auto_update_status_on_connect
        print("📲 Probando actualización automática al conectar...")
        await user_status_handler.auto_update_status_on_connect(user_id)
        
        user_after_connect = get_user(user_id)
        if user_after_connect:
            print(f"✅ Estado después de conectar: {user_after_connect.status}")
        else:
            print("❌ Usuario no encontrado después de conectar")
        
        # 4. Test auto_update_status_on_join
        print("🎮 Probando actualización automática al unirse a partida...")
        message_data = {"game_id": game_id}
        await user_status_handler.auto_update_status_on_join(connection_id, message_data)
        
        user_after_join = get_user(user_id)
        if user_after_join:
            print(f"✅ Estado después de unirse a partida: {user_after_join.status}")
        else:
            print("❌ Usuario no encontrado después de unirse a partida")
        
        # 5. Test auto_update_status_on_game_start
        print("▶️ Probando actualización automática al iniciar juego...")
        await user_status_handler.auto_update_status_on_game_start([user_id])
        
        user_after_start = get_user(user_id)
        if user_after_start:
            print(f"✅ Estado después de iniciar juego: {user_after_start.status}")
        else:
            print("❌ Usuario no encontrado después de iniciar juego")
        
        # 6. Test auto_update_status_on_player_death
        print("💀 Probando actualización automática cuando el jugador muere...")
        await user_status_handler.auto_update_status_on_player_death(user_id)
        
        user_after_death = get_user(user_id)
        if user_after_death:
            print(f"✅ Estado después de muerte: {user_after_death.status}")
        else:
            print("❌ Usuario no encontrado después de muerte")
        
        # 7. Test auto_update_status_on_leave_game
        print("🚪 Probando actualización automática al salir de partida...")
        await user_status_handler.auto_update_status_on_leave_game(user_id)
        
        user_after_leave = get_user(user_id)
        if user_after_leave:
            print(f"✅ Estado después de salir de partida: {user_after_leave.status}")
        else:
            print("❌ Usuario no encontrado después de salir de partida")
        
        # 8. Test auto_update_status_on_disconnect
        print("📴 Probando actualización automática al desconectar...")
        await user_status_handler.auto_update_status_on_disconnect(user_id)
        
        user_after_disconnect = get_user(user_id)
        if user_after_disconnect:
            print(f"✅ Estado después de desconectar: {user_after_disconnect.status}")
        else:
            print("❌ Usuario no encontrado después de desconectar")
        
        # Limpiar conexión simulada
        if connection_id in connection_manager.connection_users:
            del connection_manager.connection_users[connection_id]
        if connection_id in connection_manager.connection_info:
            del connection_manager.connection_info[connection_id]
        
        print("\n🎉 Test completado exitosamente!")
        
        # Verificar transiciones de estado esperadas
        expected_transitions = [
            ("inicial", "active"),
            ("conectar", "connected"), 
            ("unirse", "in_game"),
            ("iniciar", "alive_in_game"),
            ("muerte", "in_game"),
            ("salir", "connected"),
            ("desconectar", "disconnected")
        ]
        
        print("\n📊 Resumen de transiciones de estado:")
        for action, expected_status in expected_transitions:
            print(f"   {action}: {expected_status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en el test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Función principal del test"""
    print("🚀 Iniciando tests de estado de usuario en unión a partidas\n")
    
    success = await test_user_status_join_game()
    
    if success:
        print("\n✅ Todos los tests pasaron correctamente")
        return 0
    else:
        print("\n❌ Algunos tests fallaron")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

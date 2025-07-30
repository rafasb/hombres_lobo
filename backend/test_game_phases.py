#!/usr/bin/env python3
"""
Test completo del sistema de fases de juego con WebSocket
"""
import asyncio
import websockets
import requests
import json

async def test_game_phases():
    # Paso 1: Hacer login
    print("🔐 Haciendo login...")
    
    login_data = {
        "username": "admin",
        "password": "adminpass123"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            login_result = response.json()
            token = login_result.get("access_token")
            print("✅ Login exitoso")
        else:
            print(f"❌ Error en login: {response.status_code} - {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error conectando al backend: {e}")
        return

    # Paso 2: Conectar WebSocket
    game_id = "test-game-phases"
    uri = f"ws://localhost:8000/ws/{game_id}?token={token}"
    
    print(f"🔌 Conectando WebSocket a juego: {game_id}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket conectado!")
            
            # Paso 3: Unirse al juego
            join_message = {
                "type": "join_game",
                "game_id": game_id
            }
            
            await websocket.send(json.dumps(join_message))
            print("📤 Mensaje join_game enviado")
            
            # Recibir respuesta
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Respuesta join: {response}")
            except asyncio.TimeoutError:
                print("⏰ Timeout en join_game")
            
            # Paso 4: Iniciar juego (esto debería activar las fases)
            start_message = {
                "type": "start_game",
                "game_id": game_id
            }
            
            await websocket.send(json.dumps(start_message))
            print("📤 Mensaje start_game enviado - ¡Iniciando sistema de fases!")
            
            # Paso 5: Escuchar mensajes de fases por 30 segundos
            print("👂 Escuchando cambios de fase por 30 segundos...")
            
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < 30:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    message = json.loads(response)
                    
                    # Mostrar mensajes importantes de fases
                    if message.get("type") in ["game_started", "phase_changed", "phase_timer"]:
                        print(f"🎮 {message.get('type').upper()}: {json.dumps(message, indent=2)}")
                    elif message.get("type") == "system_message":
                        print(f"💬 SYSTEM: {message.get('message', 'Sin mensaje')}")
                    else:
                        print(f"📥 Otro mensaje: {message.get('type', 'unknown')}")
                        
                except asyncio.TimeoutError:
                    print(".", end="", flush=True)  # Mostrar progreso
                except json.JSONDecodeError:
                    print(f"❌ Error decodificando JSON: {response}")
            
            print("\n✅ Test de fases completado!")
            
    except Exception as e:
        print(f"❌ Error WebSocket: {e}")

if __name__ == "__main__":
    print("🧪 Iniciando test completo del sistema de fases...")
    asyncio.run(test_game_phases())

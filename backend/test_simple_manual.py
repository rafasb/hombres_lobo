#!/usr/bin/env python3
"""
Test simple para verificar cambio manual de fases
"""
import asyncio
import websockets
import json
import requests

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

async def test_simple_manual_phase():
    """Test simple del cambio manual"""
    print("🧪 Test simple del cambio manual de fases\n")
    
    # Setup
    response = requests.post(f"{BASE_URL}/login", data={"username": "admin", "password": "adminpass123"})
    admin_token = response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    game_data = {"name": "Simple Manual Test", "creator_id": "admin", "max_players": 6}
    response = requests.post(f"{BASE_URL}/games", headers=headers, json=game_data)
    game_id = response.json()["id"]
    print(f"✅ Juego creado: {game_id}")
    
    # Conectar
    uri = f"{WS_URL}/ws/{game_id}?token={admin_token}"
    async with websockets.connect(uri) as websocket:
        print("✅ Conectado!")
        
        # Join y start
        await websocket.send(json.dumps({"type": "join_game"}))
        await asyncio.sleep(1)
        await websocket.send(json.dumps({"type": "start_game"}))
        print("📤 Juego iniciado!")
        
        # Escuchar algunos mensajes iniciales
        for i in range(10):
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                data = json.loads(message)
                msg_type = data.get("type", "")
                
                print(f"📥 Recibido: {msg_type}")
                
                if msg_type == "game_started":
                    print("🎊 Juego iniciado - esperando 3 segundos...")
                    await asyncio.sleep(3)
                    
                    # Probar cambio manual
                    print("📤 Enviando comando force_next_phase...")
                    await websocket.send(json.dumps({"type": "force_next_phase"}))
                    
                elif msg_type == "success":
                    action = data.get("action", "")
                    message_text = data.get("message", "")
                    print(f"✅ SUCCESS: {action} - {message_text}")
                    
                elif msg_type == "error":
                    error_code = data.get("error_code", "")
                    message_text = data.get("message", "")
                    print(f"❌ ERROR: {error_code} - {message_text}")
                    
                elif msg_type == "phase_changed":
                    phase = data.get("phase", "")
                    print(f"🔄 FASE CAMBIADA: {phase}")
                    
                elif msg_type == "system_message":
                    message_text = data.get("message", "")
                    print(f"💬 SISTEMA: {message_text}")
                
            except asyncio.TimeoutError:
                print("⏰ Timeout - continuando...")
                continue
            except Exception as e:
                print(f"❌ Error: {e}")
                break
        
        print("\n✅ Test completado!")

async def main():
    await test_simple_manual_phase()

if __name__ == "__main__":
    asyncio.run(main())

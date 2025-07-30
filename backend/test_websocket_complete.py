#!/usr/bin/env python3
"""
Script completo para probar WebSocket con login automático
"""
import asyncio
import websockets
import requests
import json

async def test_websocket_with_login():
    # Paso 1: Hacer login para obtener token
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
            print(f"✅ Login exitoso, token obtenido: {token[:50]}...")
        else:
            print(f"❌ Error en login: {response.status_code} - {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error conectando al backend: {e}")
        return

    # Paso 2: Conectar WebSocket
    game_id = "test-game-123"
    uri = f"ws://localhost:8000/ws/{game_id}?token={token}"
    
    print(f"🔌 Conectando WebSocket a: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket conectado!")
            
            # Enviar mensaje de prueba
            test_message = {
                "type": "heartbeat",
                "timestamp": "2025-01-30T22:00:00Z"
            }
            
            await websocket.send(json.dumps(test_message))
            print("📤 Heartbeat enviado")
            
            # Esperar respuesta del servidor
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                print(f"📥 Respuesta del servidor: {response}")
            except asyncio.TimeoutError:
                print("⏰ Timeout esperando respuesta del servidor")
            
            # Enviar mensaje de unirse al juego
            join_message = {
                "type": "join_game",
                "game_id": game_id
            }
            
            await websocket.send(json.dumps(join_message))
            print("📤 Mensaje join_game enviado")
            
            # Esperar más respuestas
            try:
                for i in range(3):
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    print(f"📥 Mensaje {i+1}: {response}")
            except asyncio.TimeoutError:
                print("⏰ No más mensajes recibidos")
            
            print("✅ Test completado exitosamente!")
            
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ Conexión WebSocket cerrada: {e}")
    except Exception as e:
        print(f"❌ Error WebSocket: {e}")

if __name__ == "__main__":
    print("🧪 Iniciando test completo de WebSocket con login...")
    asyncio.run(test_websocket_with_login())

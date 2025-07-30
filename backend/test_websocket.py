#!/usr/bin/env python3
"""
Script de prueba para WebSocket
Prueba la conectividad básica del WebSocket server
"""
import asyncio
import websockets
import json
from app.core.security import create_access_token

async def test_websocket():
    # Crear un token de prueba
    token = create_access_token({"user_id": "test_user_123"})
    game_id = "test_game_456"
    
    uri = f"ws://localhost:8000/ws/{game_id}?token={token}"
    
    try:
        print(f"Conectando a: {uri}")
        async with websockets.connect(uri) as websocket:
            print("✅ Conectado al WebSocket!")
            
            # Enviar mensaje de prueba
            test_message = {
                "type": "get_game_status",
                "timestamp": "2025-07-30T22:00:00Z"
            }
            
            await websocket.send(json.dumps(test_message))
            print(f"📤 Mensaje enviado: {test_message}")
            
            # Recibir respuestas por 10 segundos
            try:
                for i in range(5):
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(response)
                    print(f"📥 Respuesta {i+1}: {data['type']} - {data.get('message', 'Sin mensaje')}")
                    
            except asyncio.TimeoutError:
                print("⏰ Timeout esperando más mensajes")
            
            print("✅ Test completado exitosamente!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())

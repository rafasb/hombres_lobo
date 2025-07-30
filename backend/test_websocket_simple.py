#!/usr/bin/env python3
"""
Script simple para probar la conexión WebSocket
"""
import asyncio
import websockets
import json

async def test_websocket():
    # Token de prueba (necesitarás usar un token válido)
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3NTkyNzM2ODN9.YOUR_ACTUAL_TOKEN"
    game_id = "test-game-123"
    
    uri = f"ws://localhost:8000/ws/{game_id}?token={token}"
    
    print(f"Conectando a: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Conectado al WebSocket!")
            
            # Enviar mensaje de prueba
            test_message = {
                "type": "heartbeat",
                "timestamp": "2025-01-30T22:00:00Z"
            }
            
            await websocket.send(json.dumps(test_message))
            print("📤 Mensaje enviado")
            
            # Esperar respuesta
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Respuesta recibida: {response}")
            except asyncio.TimeoutError:
                print("⏰ Timeout esperando respuesta")
            
            print("✅ Test completado exitosamente!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Iniciando test de WebSocket...")
    asyncio.run(test_websocket())

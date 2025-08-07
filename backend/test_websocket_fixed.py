#!/usr/bin/env python3
"""
Script mejorado para probar WebSocket con las correcciones aplicadas
"""
import asyncio
import websockets
from websockets.exceptions import InvalidStatusCode
import requests
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_websocket_connection():
    # Paso 1: Hacer login para obtener token
    logger.info("🔐 Haciendo login...")
    
    login_data = {
        "username": "admin",
        "password": "adminpass123"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if response.status_code == 200:
            login_result = response.json()
            token = login_result.get("access_token")
            logger.info(f"✅ Login exitoso, token obtenido")
        else:
            logger.error(f"❌ Error en login: {response.status_code} - {response.text}")
            return
            
    except Exception as e:
        logger.error(f"❌ Error conectando al backend para login: {e}")
        return

    # Paso 2: Conectar WebSocket
    game_id = "test-game-websocket"
    uri = f"ws://localhost:8000/ws/{game_id}?token={token}"
    
    logger.info(f"🔌 Conectando WebSocket a: ws://localhost:8000/ws/{game_id}")
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("✅ WebSocket conectado exitosamente!")
            
            # Test 1: Enviar heartbeat
            logger.info("📤 Enviando heartbeat...")
            heartbeat_message = {
                "type": "heartbeat",
                "timestamp": "2025-01-30T22:00:00Z"
            }
            
            await websocket.send(json.dumps(heartbeat_message))
            
            # Test 2: Unirse al juego
            logger.info("📤 Enviando join_game...")
            join_message = {
                "type": "join_game"
            }
            
            await websocket.send(json.dumps(join_message))
            
            # Test 3: Obtener estado del juego
            logger.info("📤 Enviando get_game_status...")
            status_message = {
                "type": "get_game_status"
            }
            
            await websocket.send(json.dumps(status_message))
            
            # Escuchar respuestas del servidor
            logger.info("👂 Escuchando respuestas del servidor...")
            message_count = 0
            max_messages = 10
            
            while message_count < max_messages:
                try:
                    # Esperar mensaje con timeout
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    message_count += 1
                    
                    try:
                        parsed_response = json.loads(response)
                        message_type = parsed_response.get("type", "unknown")
                        logger.info(f"📥 Mensaje {message_count}: {message_type}")
                        logger.debug(f"   Contenido: {response[:200]}...")
                        
                        # Responder a heartbeat si es necesario
                        if message_type == "heartbeat":
                            logger.info("💓 Respondiendo a heartbeat del servidor...")
                            await websocket.send(json.dumps({"type": "heartbeat"}))
                        
                    except json.JSONDecodeError:
                        logger.info(f"📥 Mensaje {message_count} (texto plano): {response[:100]}...")
                    
                except asyncio.TimeoutError:
                    logger.info("⏰ Timeout esperando más mensajes")
                    break
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("🔌 Conexión cerrada por el servidor")
                    break
            
            logger.info("✅ Test completado exitosamente!")
            logger.info(f"📊 Total de mensajes recibidos: {message_count}")
            
    except websockets.exceptions.ConnectionClosed as e:
        logger.error(f"❌ Conexión cerrada: {e.reason}")
    except InvalidStatusCode as e:
        logger.error(f"❌ Código de estado inválido: {e.status_code}")
    except Exception as e:
        logger.error(f"❌ Error WebSocket: {e}")

if __name__ == "__main__":
    logger.info("🧪 Iniciando test de WebSocket con correcciones...")
    try:
        asyncio.run(test_websocket_connection())
    except KeyboardInterrupt:
        logger.info("🛑 Test interrumpido por usuario")
    except Exception as e:
        logger.error(f"❌ Error fatal en test: {e}")

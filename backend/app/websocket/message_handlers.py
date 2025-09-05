"""
Handlers principales para mensajes WebSocket
Maneja eventos de conexión, desconexión y mensajes básicos (heartbeat)
"""
from fastapi import WebSocket, WebSocketDisconnect
from app.websocket.connection_manager import connection_manager
from app.websocket.messages_types import (
    MessageType, ErrorCode, WsMessageError, WsMessageSuccess, SystemMessage,
    WebSocketMessageV2, WsMessagePlayerId, WsSystemMessage, SystemMessageType
)
from app.websocket.user_status_handlers import user_status_handler
from app.core.security import verify_access_token
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MessageHandler:
    """Manejador principal de mensajes WebSocket"""
    
    def __init__(self):
        self.handlers = {
            MessageType.HEARTBEAT: self.handle_heartbeat,
        }
    
    async def handle_message(self, connection_id: str, message_data: dict):
        """Manejar mensaje entrante"""
        try:
            # Log incoming parsed message
            logger.info(f"RECV <- connection_id={connection_id} message={message_data}")
            # Validar estructura básica del mensaje
            if "type" not in message_data:
                await self.send_error(connection_id, ErrorCode.INVALID_MESSAGE, "Tipo de mensaje requerido")
                return
            
            message_type = MessageType(message_data["type"])
            
            # Buscar handler específico
            if message_type in self.handlers:
                await self.handlers[message_type](connection_id, message_data)
            else:
                await self.send_error(connection_id, ErrorCode.UNKNOWN_MESSAGE_TYPE, f"Tipo de mensaje no soportado: {message_type}")
                
        except ValueError as e:
            await self.send_error(connection_id, ErrorCode.INVALID_MESSAGE_TYPE, str(e))
        except Exception as e:
            logger.error(f"Error manejando mensaje de {connection_id}: {e}")
            await self.send_error(connection_id, ErrorCode.INTERNAL_ERROR, "Error interno del servidor")
    
    async def handle_heartbeat(self, connection_id: str, message_data: dict):
        """Manejar heartbeat/ping"""
        # Responder con pong usando WebSocketMessageV2
        heartbeat_response = WebSocketMessageV2(
            type=MessageType.HEARTBEAT,
            data={
                "response": "pong",
                "timestamp": message_data.get("timestamp")
            },
            timestamp=datetime.now()
        )
        await connection_manager.send_personal_message(connection_id, heartbeat_response)
            
    async def send_error(self, connection_id: str, error_code: ErrorCode, message: str, details: dict | None = None):
        """Enviar mensaje de error a conexión específica"""
        error_message = WsMessageError(
            type=MessageType.ERROR,
            error_code=error_code,
            data=message,
            timestamp=datetime.now()
        )
        # Agregar details si se proporciona
        if details:
            error_message.data = f"{message} - Details: {details}"
        
        await connection_manager.send_personal_message(
            connection_id,
            error_message
        )
    
    async def send_success(self, connection_id: str, action: str, message: str, data: dict | None = None):
        """Enviar mensaje de éxito a conexión específica"""
        success_data = message
        if data:
            success_data = f"{message} - Data: {data}"
            
        success_message = WsMessageSuccess(
            type=MessageType.SUCCESS,
            data=success_data,
            timestamp=datetime.now()
        )
        await connection_manager.send_personal_message(
            connection_id,
            success_message
        )

# Instancia global del message handler
message_handler = MessageHandler()

async def websocket_endpoint(websocket: WebSocket, game_id: str, token: str) -> None:
    """Endpoint principal de WebSocket"""
    connection_id = None
    
    try:
        logger.info(f"Intentando conectar WebSocket para juego {game_id}")
        logger.info(f"Token recibido: {token[:50]}...")
        
        # Verificar token de autenticación
        payload = verify_access_token(token)
        logger.info(f"Payload del token: {payload}")
        
        if not payload:
            logger.error("Token inválido - cerrando conexión")
            try:
                await websocket.close(code=4001, reason="Token inválido")
            except Exception:
                pass  # Si ya está cerrado, ignorar el error
            return
        
        user_id = payload.get("user_id")
        if not user_id:
            # Intentar con 'sub' como alternativa
            user_id = payload.get("sub")
            
        logger.info(f"User ID extraído: {user_id}")
        
        if not user_id:
            logger.error("Usuario no encontrado en token - cerrando conexión")
            try:
                await websocket.close(code=4001, reason="Usuario no encontrado en token")
            except Exception:
                pass  # Si ya está cerrado, ignorar el error
            return
        
        # Conectar usuario
        connection_id = await connection_manager.connect(websocket, user_id, game_id)
        logger.info(f"Usuario {user_id} conectado al juego {game_id} con conexión {connection_id}")
        
        # Actualizar estado del usuario a 'connected' automáticamente
        try:
            await user_status_handler.auto_update_status_on_connect(user_id)
        except Exception as e:
            logger.warning(f"Error actualizando estado a conectado para {user_id}: {e}")
        
        # Enviar mensaje de bienvenida usando SystemMessage
        welcome_message = WsSystemMessage(
            type=MessageType.SYSTEM_MESSAGE,
            data=f"Conectado al juego {game_id}",
            message_key=SystemMessageType.CONNECTED_TO_GAME,
            params={"game_id": game_id},
            timestamp=datetime.now()
        )
        await connection_manager.send_personal_message(
            connection_id,
            welcome_message
        )

        
        # Loop principal de mensajes
        # Los únicos mensajes que se pueden recibir son de HEARTBEAT

        while True:
            try:
                # Recibir mensaje
                data = await websocket.receive_text()
                # Log raw incoming message
                logger.info(f"RAW RECV <- connection_id={connection_id} raw={data}")
                message_data = json.loads(data)
                
                # Procesar mensaje
                await message_handler.handle_message(connection_id, message_data)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await message_handler.send_error(
                    connection_id,
                    ErrorCode.INVALID_MESSAGE,
                    "Formato JSON inválido"
                )
            except Exception as e:
                logger.error(f"Error en websocket loop: {e}")
                await message_handler.send_error(
                    connection_id,
                    ErrorCode.INTERNAL_ERROR,
                    "Error interno del servidor"
                )
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"Error en websocket endpoint: {e}")
        try:
            if websocket.client_state.name != "DISCONNECTED":
                await websocket.close(code=4000, reason="Error interno")
        except Exception:
            pass  # Si ya está cerrado, ignorar el error
    finally:
        # Limpiar conexión y actualizar estado
        if connection_id:
            user_id = await connection_manager.disconnect(connection_id)
            
            # Actualizar estado del usuario a 'disconnected' automáticamente
            if user_id:
                try:
                    await user_status_handler.auto_update_status_on_disconnect(user_id)
                except Exception as e:
                    logger.warning(f"Error actualizando estado a desconectado para {user_id}: {e}")
            
            # Limpiar recursos finales
            await connection_manager.cleanup_after_disconnect()
            logger.info(f"Conexión {connection_id} desconectada")

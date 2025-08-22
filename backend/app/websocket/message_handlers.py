"""
Handlers principales para mensajes WebSocket
Maneja eventos de conexión, desconexión y mensajes básicos
"""
from fastapi import WebSocket, WebSocketDisconnect
from app.websocket.connection_manager import connection_manager
from app.websocket.messages import (
    MessageType, ErrorMessage, SuccessMessage, SystemMessage
)
from app.websocket.game_handlers import game_handler
from app.websocket.voting_handlers import voting_handler
from app.websocket.user_status_handlers import user_status_handler
from app.core.security import verify_access_token
# from app.services.user_service import get_user
import json
import logging

logger = logging.getLogger(__name__)

class MessageHandler:
    """Manejador principal de mensajes WebSocket"""
    
    def __init__(self):
        self.handlers = {
            MessageType.HEARTBEAT: self.handle_heartbeat,
            # User status handlers
            MessageType.UPDATE_USER_STATUS: user_status_handler.handle_update_user_status,
            # Game handlers
            MessageType.JOIN_GAME: game_handler.handle_join_game,
            MessageType.START_GAME: game_handler.handle_start_game,
            MessageType.RESTART_GAME: game_handler.handle_restart_game,
            MessageType.GET_GAME_STATUS: game_handler.handle_get_game_status,
            MessageType.FORCE_NEXT_PHASE: game_handler.handle_force_next_phase,
            # Voting handlers
            MessageType.CAST_VOTE: voting_handler.handle_cast_vote,
            MessageType.GET_VOTING_STATUS: voting_handler.handle_get_voting_status,
        }
    
    async def handle_message(self, connection_id: str, message_data: dict):
        """Manejar mensaje entrante"""
        try:
            # Validar estructura básica del mensaje
            if "type" not in message_data:
                await self.send_error(connection_id, "INVALID_MESSAGE", "Tipo de mensaje requerido")
                return
            
            message_type = MessageType(message_data["type"])
            
            # Buscar handler específico
            if message_type in self.handlers:
                await self.handlers[message_type](connection_id, message_data)
            else:
                await self.send_error(connection_id, "UNKNOWN_MESSAGE_TYPE", f"Tipo de mensaje no soportado: {message_type}")
                
        except ValueError as e:
            await self.send_error(connection_id, "INVALID_MESSAGE_TYPE", str(e))
        except Exception as e:
            logger.error(f"Error manejando mensaje de {connection_id}: {e}")
            await self.send_error(connection_id, "INTERNAL_ERROR", "Error interno del servidor")
    
    async def handle_heartbeat(self, connection_id: str, message_data: dict):
        """Manejar heartbeat/ping"""
        # Responder con pong
        await connection_manager.send_personal_message(connection_id, {
            "type": MessageType.HEARTBEAT,
            "response": "pong",
            "timestamp": message_data.get("timestamp")
        })
        
    async def handle_join_game(self, connection_id: str, message_data: dict):
        """Delegar a game handler"""
        await game_handler.handle_join_game(connection_id, message_data)
        await user_status_handler.auto_update_status_on_join(connection_id, message_data)
    
    async def handle_start_game(self, connection_id: str, message_data: dict):
        """Delegar a game handler"""
        await game_handler.handle_start_game(connection_id, message_data)
    
    async def handle_get_game_status(self, connection_id: str, message_data: dict):
        """Delegar a game handler"""
        await game_handler.handle_get_game_status(connection_id, message_data)
    
    async def send_error(self, connection_id: str, error_code: str, message: str, details: dict | None = None):
        """Enviar mensaje de error a conexión específica"""
        error_message = ErrorMessage(
            error_code=error_code,
            message=message,
            details=details or {}
        )
        await connection_manager.send_personal_message(
            connection_id,
            error_message
        )
    
    async def send_success(self, connection_id: str, action: str, message: str, data: dict | None = None):
        """Enviar mensaje de éxito a conexión específica"""
        success_message = SuccessMessage(
            action=action,
            message=message,
            data=data or {}
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
        
        # Enviar mensaje de bienvenida
        welcome_message = SystemMessage(
            message=f"Conectado al juego {game_id}",
            message_key="connected_to_game",
            params={"game_id": game_id}
        )
        await connection_manager.send_personal_message(
            connection_id,
            welcome_message
        )
        
        # Loop principal de mensajes
        while True:
            try:
                # Recibir mensaje
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Procesar mensaje
                await message_handler.handle_message(connection_id, message_data)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await message_handler.send_error(
                    connection_id,
                    "INVALID_JSON",
                    "Formato JSON inválido"
                )
            except Exception as e:
                logger.error(f"Error en websocket loop: {e}")
                await message_handler.send_error(
                    connection_id,
                    "INTERNAL_ERROR",
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

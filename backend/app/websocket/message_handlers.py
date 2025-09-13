"""
Handlers principales para mensajes WebSocket
Maneja eventos de conexión, desconexión y mensajes básicos (heartbeat)
"""
from app.websocket.connection_manager import connection_manager
from app.websocket.messages_types import (
    MessageType, ErrorCode, WsMessageError, WsMessageSuccess,
)

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MessageHandler:
    """Manejador principal de mensajes WebSocket
    Depende de MessageType para enrutar a handlers específicos
    Depende de connection_manager para enviar mensajes
    """
    
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
        """Manejar heartbeat/ping del cliente"""
        print(f"💓 [HEARTBEAT] Recibido heartbeat de cliente {connection_id[:8]}...")
        logger.debug(f"Heartbeat recibido de cliente {connection_id}")
        
        # Registrar respuesta de heartbeat (esto confirma que el cliente está vivo)
        connection_manager.record_heartbeat_response(connection_id)
        
        # Verificar si incluye timestamp del cliente para logs de debug
        client_timestamp = message_data.get("timestamp")
        if client_timestamp:
            print(f"💓 [HEARTBEAT] Cliente timestamp: {client_timestamp}")
            logger.debug(f"Cliente {connection_id} timestamp: {client_timestamp}")
        
        # Obtener información del usuario para logs
        user_id = connection_manager.connection_users.get(connection_id, "unknown")
        print(f"💓 [HEARTBEAT] ✅ Cliente {user_id} ({connection_id[:8]}...) confirmado como vivo")
        logger.debug(f"Cliente {user_id} confirmado como vivo mediante heartbeat")

       
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

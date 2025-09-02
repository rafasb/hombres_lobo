from app.websocket.connection_manager import ConnectionManager, WebSocketState
from app.websocket.messages_types import (
    MessageType, ErrorMessage, SuccessMessage, SystemMessage
)
from fastapi import WebSocket
import logging
from messages_types import WebSocketMessageV2

class NotificationManager(ConnectionManager):
    '''Manejador de notificaciones WebSocket'''
    async def send_personal_message(self, connection_id: str, message: WebSocketMessageV2):
        """Enviar mensaje a conexión específica"""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            if websocket.application_state == WebSocketState.CONNECTED:
                await websocket.send_json(message.dict())
            else:
                logging.warning(f"WebSocket {connection_id} no está conectado")
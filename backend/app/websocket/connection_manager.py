"""
Connection Manager para WebSocket
Maneja conexiones, rooms de juegos y broadcast de mensajes
"""
from typing import Dict, List, Set
from fastapi import WebSocket
import json
import asyncio
import uuid
from datetime import datetime
import logging
from enum import Enum
from app.websocket.messages_types import MessageType, WsMessagePlayerId, WebSocketMessageV2 as WebSocketMessage

class WebSocketState(str, Enum):
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"

class ConnectionManager:
    def __init__(self):
        # Conexiones activas por websocket
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Información de conexiones
        self.connection_info: Dict[str, dict] = {}
        
        # Rooms de juegos: game_id -> set of connection_ids
        self.game_rooms: Dict[str, Set[str]] = {}
        
        # Usuario por conexión: connection_id -> user_id
        self.connection_users: Dict[str, str] = {}
        
        # Heartbeat para mantener conexiones vivas
        self.heartbeat_task = None
        self.logger = logging.getLogger("websocket.connection_manager")

    def _normalize_message(self, connection_id , message: WebSocketMessage) -> str:
        # Normalizar mensaje: asumimos WebSocketMessage (pydantic). Si falla, usar fallback sencillo.
        # connection_id es solo para logging, puede ser un broadcast.
        try:
            message_dict = message.model_dump()
        except Exception:
            message_dict = {"message": str(message)}

        # Asegurar campo type mínimo
        if "type" not in message_dict:
            message_dict["type"] = "system_message"

        message_text = json.dumps(message_dict, default=str)

        connection_id_safe = connection_id if connection_id else "N/A"

        try:
            self.logger.info(f"SEND -> connection_id={connection_id_safe} message={message_text}")
        except Exception:
            print(f"SEND -> connection_id={connection_id_safe} message={message_text}")

        return message_text

    async def connect(self, websocket: WebSocket, user_id: str, game_id: str | None = None):
        """Conectar un cliente WebSocket"""
        await websocket.accept()
        
        # Generar ID único para la conexión
        connection_id = str(uuid.uuid4())
        
        # Registrar conexión
        self.active_connections[connection_id] = websocket
        self.connection_users[connection_id] = user_id
        
        # Información de conexión
        now = datetime.now()
        self.connection_info[connection_id] = {
            "user_id": user_id,
            "game_id": game_id,
            "connected_at": now,
            "last_heartbeat": now
        }
        
        # Unir a room de juego si se especifica
        if game_id:
            await self.join_game_room(connection_id, game_id)
        
        # Iniciar heartbeat si es la primera conexión
        if len(self.active_connections) == 1 and not self.heartbeat_task:
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        # Notificar cambio de estado a conectado (se llama desde websocket_endpoint)
        return connection_id

    async def disconnect(self, connection_id: str):
        """Desconectar un cliente"""
        user_id = None
        if connection_id in self.active_connections:
            # Obtener user_id antes de limpiar
            user_id = self.connection_users.get(connection_id)
            # Remover de rooms de juego
            for game_id, connections in self.game_rooms.items():
                if connection_id in connections:
                    connections.remove(connection_id)
                    
                    # Notificar a otros en la room (user_id ya fue obtenido arriba)
                    if user_id:
                        await self.broadcast_to_game(
                            game_id, 
                            WsMessagePlayerId(
                                type=MessageType.PLAYER_LEFT_GAME,
                                data=user_id), 
                            exclude_connection=connection_id)
            
            # Limpiar registros
            del self.active_connections[connection_id]
            del self.connection_info[connection_id]
            if connection_id in self.connection_users:
                del self.connection_users[connection_id]
        
        # Retornar user_id para llamadas externas de actualización de estado
        return user_id
        
    async def cleanup_after_disconnect(self):
        """Limpiar recursos después de desconexión"""
        # Detener heartbeat si no hay conexiones
        if len(self.active_connections) == 0 and self.heartbeat_task:
            self.heartbeat_task.cancel()
            self.heartbeat_task = None

    async def join_game_room(self, connection_id: str, game_id: str):
        """Unir conexión a room de juego"""
        if game_id not in self.game_rooms:
            self.game_rooms[game_id] = set()
        
        self.game_rooms[game_id].add(connection_id)
        
        # Actualizar info de conexión
        if connection_id in self.connection_info:
            self.connection_info[connection_id]["game_id"] = game_id
        
        # Notificar a otros en la room
        user_id = self.connection_users.get(connection_id)
        if user_id:
            await self.broadcast_to_game(
                game_id, 
                WsMessagePlayerId(
                    type=MessageType.IN_GAME,
                    data=user_id),
                exclude_connection=connection_id)

    async def leave_game_room(self, connection_id: str, game_id: str):
        """Salir de room de juego"""
        if game_id in self.game_rooms and connection_id in self.game_rooms[game_id]:
            self.game_rooms[game_id].remove(connection_id)
            
            # Notificar salida
            user_id = self.connection_users.get(connection_id)
            if user_id:
                await self.broadcast_to_game(
                    game_id,
                    WsMessagePlayerId(
                        type=MessageType.PLAYER_LEFT_GAME,
                        data=user_id),
                )

    async def send_personal_message(self, connection_id: str, message: WebSocketMessage):
        if connection_id not in self.active_connections:
            return
        websocket = self.active_connections.get(connection_id)
        try:
            if not websocket or websocket.client_state.name != "CONNECTED":
                self.logger.debug(f"WebSocket {connection_id} no está conectado, removiendo de conexiones activas")
                await self.disconnect(connection_id)
                return

            message_text = self._normalize_message(connection_id, message)

            await websocket.send_text(message_text)

        except Exception:
            # Loguear stacktrace y desconectar en caso de error
            self.logger.exception(f"Error enviando mensaje personal a {connection_id}")
            await self.disconnect(connection_id)

    async def broadcast_to_game(self, game_id: str, message: WebSocketMessage, exclude_connection: str | None = None):
        """Broadcast mensaje a todos en un juego"""
        if game_id not in self.game_rooms:
            return
        # Normalizar mensaje similar a send_personal_message
        message_text = self._normalize_message(f'broadcast-{game_id}', message)

        try:
            self.logger.info(f"BROADCAST game={game_id} exclude={exclude_connection} message={message_text}")
        except Exception:
            print(f"BROADCAST game={game_id} exclude={exclude_connection} message={message_text}")

        disconnected_connections = []

        # Iterar sobre copia para evitar RuntimeError si la room cambia mientras iteramos
        for connection_id in list(self.game_rooms[game_id]):
            if connection_id == exclude_connection:
                continue

            websocket = self.active_connections.get(connection_id)
            if not websocket:
                disconnected_connections.append(connection_id)
                continue

            try:
                if getattr(websocket, "client_state", None) and websocket.client_state.name == "CONNECTED":
                    await websocket.send_text(message_text)
                else:
                    disconnected_connections.append(connection_id)
            except Exception:
                self.logger.exception(f"Error enviando mensaje a conexión {connection_id}")
                disconnected_connections.append(connection_id)

        for connection_id in disconnected_connections:
            await self.disconnect(connection_id)

    async def broadcast_to_all(self, message: WebSocketMessage):
        """Broadcast mensaje a todas las conexiones activas"""
        message_text = self._normalize_message("broadcast_all", message)
        
        # Log broadcast to all
        try:
            self.logger.info(f"BROADCAST_ALL message={message_text}")
        except Exception:
            print(f"BROADCAST_ALL message={message_text}")
            
        disconnected_connections = []
        
        for connection_id, websocket in self.active_connections.items():
            try:
                # Verificar el estado del WebSocket antes de enviar
                if websocket.client_state.name == "CONNECTED":
                    await websocket.send_text(message_text)
                else:
                    # WebSocket no está conectado, marcarlo para desconexión
                    disconnected_connections.append(connection_id)
            except Exception as e:
                print(f"Error broadcasting a todos {connection_id}: {e}")
                disconnected_connections.append(connection_id)
        
        # Limpiar conexiones muertas
        for connection_id in disconnected_connections:
            await self.disconnect(connection_id)

    def get_game_connections(self, game_id: str) -> List[str]:
        """Obtener lista de conexiones en un juego"""
        return list(self.game_rooms.get(game_id, set()))

    def get_game_users(self, game_id: str) -> List[str]:
        """Obtener lista de usuarios en un juego"""
        connection_ids = self.get_game_connections(game_id)
        return [self.connection_users[conn_id] for conn_id in connection_ids 
                if conn_id in self.connection_users]

    def get_connection_info(self, connection_id: str) -> dict:
        """Obtener información de una conexión"""
        return self.connection_info.get(connection_id, {})

    def is_user_connected(self, user_id: str, game_id: str | None = None) -> bool:
        """Verificar si un usuario está conectado"""
        for conn_id, conn_user_id in self.connection_users.items():
            if conn_user_id == user_id:
                if game_id:
                    conn_info = self.connection_info.get(conn_id, {})
                    return conn_info.get("game_id") == game_id
                return True
        return False

    async def _heartbeat_loop(self):
        """Loop de heartbeat para mantener conexiones vivas"""
        while True:
            try:
                await asyncio.sleep(30)  # Heartbeat cada 30 segundos
                
                current_time = datetime.now()
                disconnected_connections = []
                
                for connection_id, websocket in self.active_connections.items():
                    try:
                        # Verificar el estado del WebSocket antes de enviar
                        if websocket.client_state.name == "CONNECTED":
                            # Enviar ping
                            data = WebSocketMessage(
                                type=MessageType.HEARTBEAT,
                                data={}).model_dump()
                            await websocket.send_text(json.dumps(data))
                            
                            # Actualizar último heartbeat
                            if connection_id in self.connection_info:
                                self.connection_info[connection_id]["last_heartbeat"] = current_time
                        else:
                            # WebSocket no está conectado, marcarlo para desconexión
                            disconnected_connections.append(connection_id)
                            
                    except Exception as e:
                        print(f"Heartbeat failed para {connection_id}: {e}")
                        disconnected_connections.append(connection_id)
                
                # Limpiar conexiones muertas
                for connection_id in disconnected_connections:
                    await self.disconnect(connection_id)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error en heartbeat loop: {e}")

# Instancia global del connection manager
connection_manager = ConnectionManager()

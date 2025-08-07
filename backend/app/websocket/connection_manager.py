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

    async def connect(self, websocket: WebSocket, user_id: str, game_id: str | None = None):
        """Conectar un cliente WebSocket"""
        await websocket.accept()
        
        # Generar ID único para la conexión
        connection_id = str(uuid.uuid4())
        
        # Registrar conexión
        self.active_connections[connection_id] = websocket
        self.connection_users[connection_id] = user_id
        
        # Información de conexión
        self.connection_info[connection_id] = {
            "user_id": user_id,
            "game_id": game_id,
            "connected_at": datetime.now(),
            "last_heartbeat": datetime.now()
        }
        
        # Unir a room de juego si se especifica
        if game_id:
            await self.join_game_room(connection_id, game_id)
        
        # Iniciar heartbeat si es la primera conexión
        if len(self.active_connections) == 1 and not self.heartbeat_task:
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        return connection_id

    async def disconnect(self, connection_id: str):
        """Desconectar un cliente"""
        if connection_id in self.active_connections:
            # Remover de rooms de juego
            for game_id, connections in self.game_rooms.items():
                if connection_id in connections:
                    connections.remove(connection_id)
                    
                    # Notificar a otros en la room
                    user_id = self.connection_users.get(connection_id)
                    if user_id:
                        await self.broadcast_to_game(game_id, {
                            "type": "player_disconnected",
                            "user_id": user_id,
                            "timestamp": datetime.now().isoformat()
                        }, exclude_connection=connection_id)
            
            # Limpiar registros
            del self.active_connections[connection_id]
            del self.connection_info[connection_id]
            if connection_id in self.connection_users:
                del self.connection_users[connection_id]
        
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
            await self.broadcast_to_game(game_id, {
                "type": "player_connected",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }, exclude_connection=connection_id)

    async def leave_game_room(self, connection_id: str, game_id: str):
        """Salir de room de juego"""
        if game_id in self.game_rooms and connection_id in self.game_rooms[game_id]:
            self.game_rooms[game_id].remove(connection_id)
            
            # Notificar salida
            user_id = self.connection_users.get(connection_id)
            if user_id:
                await self.broadcast_to_game(game_id, {
                    "type": "player_left_game",
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat()
                })

    async def send_personal_message(self, connection_id: str, message):
        """Enviar mensaje a conexión específica"""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                # Verificar el estado del WebSocket antes de enviar
                if websocket.client_state.name != "CONNECTED":
                    print(f"WebSocket {connection_id} no está conectado, removiendo de conexiones activas")
                    await self.disconnect(connection_id)
                    return
                
                # Si el mensaje es un modelo Pydantic, usar su serialización
                # Si es un dict simple, serializarlo con json.dumps
                if hasattr(message, 'json'):
                    message_text = message.json()
                else:
                    message_text = json.dumps(message, default=str)
                await websocket.send_text(message_text)
            except Exception as e:
                print(f"Error enviando mensaje personal a {connection_id}: {e}")
                await self.disconnect(connection_id)

    async def broadcast_to_game(self, game_id: str, message, exclude_connection: str | None = None):
        """Broadcast mensaje a todos en un juego"""
        if game_id not in self.game_rooms:
            return
        
        # Agregar game_id al mensaje si es un dict
        if isinstance(message, dict):
            message["game_id"] = game_id
            message_text = json.dumps(message, default=str)
        else:
            # Si es un modelo Pydantic, agregar game_id a través del dict
            if hasattr(message, 'dict'):
                message_dict = message.dict()
                message_dict["game_id"] = game_id
                message_text = json.dumps(message_dict, default=str)
            else:
                message_text = message.json() if hasattr(message, 'json') else str(message)
        
        disconnected_connections = []
        
        for connection_id in self.game_rooms[game_id]:
            if connection_id != exclude_connection and connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                try:
                    # Verificar el estado del WebSocket antes de enviar
                    if websocket.client_state.name == "CONNECTED":
                        await websocket.send_text(message_text)
                    else:
                        # WebSocket no está conectado, marcarlo para desconexión
                        disconnected_connections.append(connection_id)
                except Exception as e:
                    print(f"Error enviando mensaje a conexión {connection_id}: {e}")
                    disconnected_connections.append(connection_id)
        
        # Limpiar conexiones muertas
        for connection_id in disconnected_connections:
            await self.disconnect(connection_id)

    async def broadcast_to_all(self, message):
        """Broadcast mensaje a todas las conexiones activas"""
        if hasattr(message, 'json'):
            message_text = message.json()
        else:
            message_text = json.dumps(message, default=str)
            
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
                            await websocket.send_text(json.dumps({
                                "type": "heartbeat",
                                "timestamp": current_time.isoformat()
                            }))
                            
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

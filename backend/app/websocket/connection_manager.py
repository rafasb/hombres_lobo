"""
Connection Manager para WebSocket
Maneja conexiones, rooms de juegos y broadcast de mensajes
Métodos Pricipales:
- connect(websocket, user_id, game_id=None) -> connection_id
- disconnect(connection_id)
- send_personal_message(connection_id, message)
- broadcast_to_game(game_id, message, exclude_connection=None)
- broadcast_to_all(message)
- join_game_room(connection_id, game_id)
- leave_game_room(connection_id, game_id)
- get_game_connections(game_id) -> List[connection_id]
- get_game_users(game_id) -> List[user_id]
- is_user_connected(user_id, game_id=None) -> bool
- get_connection_info(connection_id) -> dict
- cleanup_after_disconnect()
- _heartbeat_loop()  # Tarea interna para mantener conexiones vivas
"""
from typing import Dict, List, Set
from fastapi import WebSocket
import json
import asyncio
import uuid
from datetime import datetime
import logging
from enum import Enum
from app.websocket.messages_types import MessageType, UserIdName, WsMessagePlayerId, WebSocketMessageV2 as WebSocketMessage
from app.services.user_service import UserService, UserStatus, UserStatusUpdate
from app.services.game_state_service import game_state_manager

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
        # Nuevos contadores para estadísticas de heartbeat
        self.heartbeat_stats = {
            "sent": 0,
            "responses_received": 0,
            "failed_connections": 0,
            "last_heartbeat_time": None
        }
        print("ConnectionManager inicializado")


    def _normalize_message(self, connection_id , message: WebSocketMessage) -> str:
        # Normalizar mensaje: asumimos WebSocketMessage (pydantic). Si falla, usar fallback sencillo.
        # connection_id es solo para logging, puede ser un broadcast.
        try:
            # Usar model_dump_json() que maneja automáticamente la serialización de datetime
            message_text = message.model_dump_json()
        except Exception:
            # Fallback para mensajes que no son pydantic
            try:
                message_dict = {"message": str(message), "type": str(MessageType.SYSTEM_MESSAGE)}
                message_text = json.dumps(message_dict, default=str)
            except Exception:
                message_text = json.dumps({"message": "Error serializing message", "type": str(MessageType.ERROR)})

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
        
        print(f"[WEBSOCKET] WebSocket conectado: connection_id={connection_id}, user_id={user_id}, game_id={game_id}")

        # Notificar cambio de estado a conectado (se llama desde websocket_endpoint)
        return connection_id

    async def disconnect(self, connection_id: str):
        """Desconectar un cliente"""
        user_id = None
        if connection_id in self.active_connections:
            # Obtener user_id antes de limpiar
            user_id = self.connection_users.get(connection_id)
            try:
                # Modificar el estado de usuario a 'disconnected' en la base de datos
                new_user_state = UserStatusUpdate(
                    status=UserStatus.DISCONNECTED
                )
                if user_id:
                    UserService.update_user_status(user_id, new_user_state)
            except Exception as e:
                self.logger.error(f"Error actualizando estado de usuario {user_id} a DISCONNECTED: {e}")
                print(f"[WEBSOCKET] Error actualizando estado de usuario {user_id} a DISCONNECTED: {e}")
            # Remover de rooms de juego
            for game_id, connections in self.game_rooms.items():
                if connection_id in connections:
                    connections.remove(connection_id)
                    
                    # Notificar a otros en la room (user_id ya fue obtenido arriba)
                    if user_id:
                        await self.broadcast_to_game(
                            game_id, 
                            WsMessagePlayerId(
                                type=MessageType.PLAYER_DISCONNECTED,
                                data=UserIdName(id=user_id, name="")
                            ),  # Nombre no disponible aquí
                            exclude_connection=connection_id)        

            # Limpiar registros
            del self.active_connections[connection_id]
            del self.connection_info[connection_id]
            if connection_id in self.connection_users:
                del self.connection_users[connection_id]
        print(f"WebSocket desconectado: connection_id={connection_id}, user_id={user_id}")
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
        
        # Actualizar estado del usuario a IN_GAME cuando se une a una partida
        user_id = self.connection_users.get(connection_id)
        if user_id:
            try:
                new_user_state = UserStatusUpdate(
                    status=UserStatus.IN_GAME,
                    game_id=game_id,
                )
                UserService.update_user_status(user_id, new_user_state)
                print(f"✅ Usuario {user_id} actualizado a estado IN_GAME en partida {game_id}")
            except Exception as e:
                self.logger.error(f"Error actualizando estado de usuario {user_id} a IN_GAME: {e}")
                print(f"❌ Error actualizando estado de usuario {user_id} a IN_GAME: {e}")
            
            # Sincronizar connected_players con el estado real
            await self.sync_connected_players_with_game_state(game_id)
            
            # Notificar a otros en la room
            await self.broadcast_to_game(
                game_id, 
                WsMessagePlayerId(
                    type=MessageType.PLAYER_CONNECTED,
                    data=UserIdName(id=user_id, name="")),
                exclude_connection=connection_id)
            print(f"Usuario {user_id} se unió a room de juego {game_id}")

    async def leave_game_room(self, connection_id: str, game_id: str):
        """Salir de room de juego"""
        if game_id in self.game_rooms and connection_id in self.game_rooms[game_id]:
            self.game_rooms[game_id].remove(connection_id)
            
            # Actualizar estado del usuario a DISCONNECTED cuando abandona la partida
            user_id = self.connection_users.get(connection_id)
            if user_id:
                try:
                    new_user_state = UserStatusUpdate(
                        status=UserStatus.DISCONNECTED,
                        game_id=None,  # Limpiar game_id al abandonar
                    )
                    UserService.update_user_status(user_id, new_user_state)
                    print(f"✅ Usuario {user_id} actualizado a estado DISCONNECTED al abandonar partida {game_id}")
                except Exception as e:
                    self.logger.error(f"Error actualizando estado de usuario {user_id} a DISCONNECTED: {e}")
                    print(f"❌ Error actualizando estado de usuario {user_id} a DISCONNECTED: {e}")
                
                # Sincronizar connected_players con el estado real
                await self.sync_connected_players_with_game_state(game_id)
                
                # Notificar salida
                await self.broadcast_to_game(
                    game_id,
                    WsMessagePlayerId(
                        type=MessageType.PLAYER_DISCONNECTED,
                        data=UserIdName(id=user_id, name="")),
                )
                print(f"Usuario {user_id} salió de room de juego {game_id}")

    async def send_personal_message(self, connection_id: str, message: WebSocketMessage):
        if connection_id not in self.active_connections:
            return
        websocket = self.active_connections.get(connection_id)
        message_text=''
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

        print(f"[WEBSOCKET] Mensaje personal enviado a connection_id={connection_id} tipo {message.type}. Contenido completo: {message_text}")

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

        print(f"Broadcast enviado a game_id={game_id}, excluyendo connection_id={exclude_connection}")

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

        print("Broadcast enviado a todas las conexiones activas")

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
    
    def get_connection_id_from_user_id(self, user_id: str) -> str | None:
        """Obtener connection_id a partir de user_id (asume un solo connection_id por user_id)"""
        for conn_id, conn_user_id in self.connection_users.items():
            if conn_user_id == user_id:
                return conn_id
        return None

    def is_user_connected(self, user_id: str, game_id: str | None = None) -> bool:
        """Verificar si un usuario está conectado"""
        for conn_id, conn_user_id in self.connection_users.items():
            if conn_user_id == user_id:
                if game_id:
                    conn_info = self.connection_info.get(conn_id, {})
                    return conn_info.get("game_id") == game_id
                return True
        return False

    async def sync_connected_players_with_game_state(self, game_id: str):
        """
        Sincroniza connected_players del objeto Game con el estado real del connection_manager
        """
        try:
            
            # Obtener usuarios realmente conectados desde game_rooms
            actual_connected_users = self.get_game_users(game_id)
            
            # Actualizar connected_players en el GameState
            await game_state_manager.update_connected_players_from_list(game_id, actual_connected_users)
            
            print(f"🔄 Sincronizados {len(actual_connected_users)} jugadores conectados en partida {game_id}")
            self.logger.info(f"Sincronizados connected_players para partida {game_id}: {actual_connected_users}")
            
        except Exception as e:
            self.logger.error(f"Error sincronizando connected_players para partida {game_id}: {e}")
            print(f"❌ Error sincronizando connected_players para partida {game_id}: {e}")

    async def _heartbeat_loop(self):
        """Loop de heartbeat para mantener conexiones vivas"""
        print("🫀 [HEARTBEAT] Iniciando heartbeat loop")
        self.logger.info("Heartbeat loop iniciado")

        while True:
            try:
                await asyncio.sleep(30)  # Heartbeat cada 30 segundos
                
                current_time = datetime.now()
                disconnected_connections = []
                
                # Log inicio de ronda de heartbeat
                active_count = len(self.active_connections)
                print(f"🫀 [HEARTBEAT] Iniciando ronda de heartbeat - {active_count} conexiones activas")
                self.logger.info(f"Iniciando ronda de heartbeat para {active_count} conexiones")
                
                disconnected_connections = []
                heartbeat_sent_count = 0

                for connection_id, websocket in self.active_connections.items():
                    try:
                        # Obtener información del usuario para logs más informativos
                        user_id = self.connection_users.get(connection_id, "unknown")
                        conn_info = self.connection_info.get(connection_id, {})
                        game_id = conn_info.get("game_id", "no_game")

                        # Verificar el estado del WebSocket antes de enviar
                        if websocket.client_state.name == "CONNECTED":
                            # Enviar ping
                            heartbeat_message = WebSocketMessage(
                                type=MessageType.HEARTBEAT,
                                data={
                                    "timestamp": current_time.isoformat(),
                                    "connection_id": connection_id
                                })
                            
                            # Usar el json_encoder de Pydantic para manejar datetime
                            message_data = heartbeat_message.model_dump_json()
                            await websocket.send_text(message_data)
                            heartbeat_sent_count += 1
                            self.heartbeat_stats["sent"] += 1

                            # Log exitoso
                            print(f"🫀 [HEARTBEAT] ✅ Enviado a user_id={user_id}, connection_id={connection_id[:8]}..., game_id={game_id}")
                            self.logger.debug(f"Heartbeat enviado a user_id={user_id}, connection_id={connection_id}")

                            # Actualizar último heartbeat
                            if connection_id in self.connection_info:
                                self.connection_info[connection_id]["last_heartbeat"] = current_time
                        else:
                            # WebSocket no está conectado, marcarlo para desconexión
                            # WebSocket no está conectado
                            print(f"🫀 [HEARTBEAT] ❌ WebSocket desconectado: user_id={user_id}, connection_id={connection_id[:8]}..., estado={websocket.client_state.name}")
                            self.logger.warning(f"WebSocket {connection_id} no conectado, estado: {websocket.client_state.name}")
                            disconnected_connections.append(connection_id)
                            
                    except Exception as e:
                        user_id = self.connection_users.get(connection_id, "unknown")
                        print(f"🫀 [HEARTBEAT] 💥 Error enviando heartbeat a user_id={user_id}, connection_id={connection_id[:8]}...: {e}")
                        self.logger.error(f"Heartbeat failed para connection_id={connection_id}, user_id={user_id}: {e}")
                        disconnected_connections.append(connection_id)
                        self.heartbeat_stats["failed_connections"] += 1

                
                # Limpiar conexiones muertas
                cleaned_count = 0
                for connection_id in disconnected_connections:
                    user_id = await self.disconnect(connection_id)
                    cleaned_count += 1
                    print(f"🫀 [HEARTBEAT] 🧹 Conexión limpiada: user_id={user_id}, connection_id={connection_id[:8]}...")

                # Log resumen de la ronda
                remaining_connections = len(self.active_connections)
                print(f"🫀 [HEARTBEAT] 📊 Ronda completada: {heartbeat_sent_count} enviados, {cleaned_count} desconectados, {remaining_connections} activas")
                self.logger.info(f"Ronda heartbeat completada: {heartbeat_sent_count} enviados, {cleaned_count} limpiadas, {remaining_connections} restantes")
                
                # Log estadísticas cada 10 rondas (5 minutos)
                if self.heartbeat_stats["sent"] % 10 == 0 and self.heartbeat_stats["sent"] > 0:
                    self._log_heartbeat_statistics()


                    
            except asyncio.CancelledError:
                print("🫀 [HEARTBEAT] ⏹️ Heartbeat loop cancelado")
                self.logger.info("Heartbeat loop cancelado")
                break
            except Exception as e:
                print(f"🫀 [HEARTBEAT] 💥 Error crítico en heartbeat loop: {e}")
                self.logger.error(f"Error crítico en heartbeat loop: {e}")
        
    def _log_heartbeat_statistics(self):
        """Log estadísticas periódicas de heartbeat"""
        stats = self.heartbeat_stats
        success_rate = 0
        if stats["sent"] > 0:
            success_rate = ((stats["sent"] - stats["failed_connections"]) / stats["sent"]) * 100
        
        print(f"🫀 [HEARTBEAT] 📈 ESTADÍSTICAS - Enviados: {stats['sent']}, Respuestas: {stats['responses_received']}, Fallos: {stats['failed_connections']}, Éxito: {success_rate:.1f}%")
        self.logger.info(f"Estadísticas heartbeat - Enviados: {stats['sent']}, Respuestas: {stats['responses_received']}, Fallos: {stats['failed_connections']}, Tasa éxito: {success_rate:.1f}%")

    def record_heartbeat_response(self, connection_id: str):
        """Registrar respuesta de heartbeat recibida"""
        self.heartbeat_stats["responses_received"] += 1
        user_id = self.connection_users.get(connection_id, "unknown")
        conn_info = self.connection_info.get(connection_id, {})
        game_id = conn_info.get("game_id", "no_game")
        
        print(f"🫀 [HEARTBEAT] 💓 Respuesta recibida de user_id={user_id}, connection_id={connection_id[:8]}..., game_id={game_id}")
        self.logger.debug(f"Heartbeat response recibida de user_id={user_id}, connection_id={connection_id}")
        
        # Actualizar timestamp de respuesta
        if connection_id in self.connection_info:
            self.connection_info[connection_id]["last_heartbeat_response"] = datetime.now()

# Instancia global del connection manager
connection_manager = ConnectionManager()

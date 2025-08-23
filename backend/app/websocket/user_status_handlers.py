"""
Handlers para gestión de estado de usuarios via WebSocket
Maneja cambios de estado automáticos y notificaciones en tiempo real
"""
from app.websocket.connection_manager import connection_manager
from app.websocket.messages import (
    UserStatusChangedMessage, ErrorMessage, SuccessMessage
)
from app.services.user_service import update_user_status
from app.models.user import UserStatusUpdate, UserStatus
import logging

logger = logging.getLogger(__name__)

class UserStatusHandler:
    """Manejador para cambios de estado de usuarios"""
    
    def __init__(self):
        self.status_mapping = {
            "connected": UserStatus.CONNECTED,
            "disconnected": UserStatus.DISCONNECTED,
            "banned": UserStatus.BANNED,
            "in_game": UserStatus.IN_GAME,
        }
    
    async def handle_update_user_status(self, connection_id: str, message_data: dict):
        """Manejar solicitud de cambio de estado"""
        try:
            # Validar campos requeridos
            if "status" not in message_data:
                await self.send_error(connection_id, "MISSING_FIELD", "Campo 'status' requerido")
                return
            
            # Obtener información de conexión
            conn_info = connection_manager.get_connection_info(connection_id)
            if not conn_info:
                await self.send_error(connection_id, "INVALID_CONNECTION", "Conexión no encontrada")
                return
            
            user_id = conn_info.get("user_id")
            if not user_id:
                await self.send_error(connection_id, "INVALID_USER", "Usuario no identificado")
                return
            
            # Validar estado solicitado
            requested_status = message_data["status"]
            if requested_status not in self.status_mapping:
                await self.send_error(connection_id, "INVALID_STATUS", f"Estado inválido: {requested_status}")
                return
            
            # Validar permisos: solo admins pueden banear usuarios
            if requested_status == "banned":
                # Obtener información del usuario para verificar si es admin
                from app.services.user_service import get_user
                user = get_user(user_id)
                if not user or user.role.value != "admin":
                    await self.send_error(connection_id, "INSUFFICIENT_PERMISSIONS", "Solo los administradores pueden banear usuarios")
                    return
            
            # Crear objeto de actualización
            status_update = UserStatusUpdate(status=self.status_mapping[requested_status])
            
            # Actualizar estado en la base de datos
            updated_user, old_status = update_user_status(user_id, status_update)
            
            if not updated_user or old_status is None:
                await self.send_error(connection_id, "UPDATE_FAILED", "Error al actualizar estado del usuario")
                return
            
            # Notificar al usuario que solicitó el cambio
            await connection_manager.send_personal_message(connection_id, SuccessMessage(
                action="update_user_status",
                message=f"Estado actualizado de '{old_status.value}' a '{requested_status}'",
                data={
                    "user_id": user_id,
                    "old_status": old_status.value,
                    "new_status": requested_status,
                    "updated_at": updated_user.updated_at.isoformat()
                }
            ))
            
            # Notificar cambio de estado a otros usuarios conectados
            await self.broadcast_status_change(
                user_id, 
                old_status.value, 
                requested_status,
                exclude_connection=connection_id
            )
            
        except Exception as e:
            logger.error(f"Error actualizando estado de usuario para {connection_id}: {e}")
            await self.send_error(connection_id, "INTERNAL_ERROR", "Error interno del servidor")
    
    async def auto_update_status_on_connect(self, user_id: str):
        """Actualizar automáticamente el estado a 'connected' cuando se conecta"""
        try:
            # Nuevo comportamiento: al conectar al websocket, marcar como IN_GAME
            status_update = UserStatusUpdate(status=UserStatus.IN_GAME)
            updated_user, old_status = update_user_status(user_id, status_update)

            if updated_user and old_status:
                # Notificar cambio de estado a otros usuarios
                await self.broadcast_status_change(
                    user_id,
                    old_status.value,
                    "in_game"
                )
                logger.info(f"Usuario {user_id} automáticamente marcado como 'in_game' al conectar")
        except Exception as e:
            logger.error(f"Error actualizando estado automático de conexión para {user_id}: {e}")
    
    async def auto_update_status_on_disconnect(self, user_id: str):
        """Actualizar automáticamente el estado a 'disconnected' cuando se desconecta"""
        try:
            # Verificar si el usuario tiene otras conexiones activas
            user_connections = [
                conn_id for conn_id, conn_user_id in connection_manager.connection_users.items()
                if conn_user_id == user_id
            ]
            
            # Solo actualizar a disconnected si no hay otras conexiones del mismo usuario
            if len(user_connections) <= 1:  # <= 1 porque la conexión actual aún no se ha removido
                # Nuevo comportamiento: al desconectar del websocket, marcar como CONNECTED
                status_update = UserStatusUpdate(status=UserStatus.CONNECTED)
                updated_user, old_status = update_user_status(user_id, status_update)

                if updated_user and old_status:
                    # Notificar cambio de estado a otros usuarios
                    await self.broadcast_status_change(
                        user_id,
                        old_status.value,
                        "active"
                    )
                    logger.info(f"Usuario {user_id} automáticamente marcado como 'active' al desconectar")
        except Exception as e:
            logger.error(f"Error actualizando estado automático de desconexión para {user_id}: {e}")
    
    async def auto_update_status_on_join(self, connection_id: str, message_data: dict):
        """Actualizar automáticamente el estado a 'in_game' cuando se une a una partida"""
        try:
            # Obtener información de conexión
            conn_info = connection_manager.get_connection_info(connection_id)
            if not conn_info:
                logger.error(f"No se encontró información de conexión para {connection_id}")
                return
            
            user_id = conn_info.get("user_id")
            game_id = message_data.get("game_id") or conn_info.get("game_id")
            
            if not user_id:
                logger.error(f"No se encontró user_id para la conexión {connection_id}")
                return
            
            if not game_id:
                logger.error("No se encontró game_id para unirse a la partida")
                return
            
            # Actualizar estado a 'in_game'
            status_update = UserStatusUpdate(status=UserStatus.IN_GAME)
            updated_user, old_status = update_user_status(user_id, status_update)
            
            if updated_user and old_status:
                # Notificar cambio de estado a otros usuarios
                await self.broadcast_status_change(
                    user_id, 
                    old_status.value, 
                    "in_game"
                )
                logger.info(f"Usuario {user_id} automáticamente marcado como 'in_game' al unirse a partida {game_id}")
            else:
                logger.warning(f"No se pudo actualizar estado para usuario {user_id}")
                
        except Exception as e:
            logger.error(f"Error actualizando estado automático al unirse a partida para {connection_id}: {e}")
    
    async def auto_update_status_on_leave_game(self, user_id: str):
        """Actualizar automáticamente el estado a 'connected' cuando sale de una partida"""
        try:
            # Actualizar estado de 'in_game' de vuelta a 'connected'
            status_update = UserStatusUpdate(status=UserStatus.CONNECTED)
            updated_user, old_status = update_user_status(user_id, status_update)
            
            if updated_user and old_status:
                # Notificar cambio de estado a otros usuarios
                await self.broadcast_status_change(
                    user_id, 
                    old_status.value, 
                    "connected"
                )
                logger.info(f"Usuario {user_id} automáticamente marcado como 'connected' al salir de la partida")
            else:
                logger.warning(f"No se pudo actualizar estado para usuario {user_id} al salir de partida")
                
        except Exception as e:
            logger.error(f"Error actualizando estado automático al salir de partida para {user_id}: {e}")
    
    async def auto_update_status_on_game_start(self, user_ids: list[str]):
        """Actualizar automáticamente el estado a 'in_game' cuando inicia la partida"""
        try:
            for user_id in user_ids:
                # Actualizar estado a 'in_game'
                status_update = UserStatusUpdate(status=UserStatus.IN_GAME)
                updated_user, old_status = update_user_status(user_id, status_update)
                
                if updated_user and old_status:
                    # Notificar cambio de estado a otros usuarios
                    await self.broadcast_status_change(
                        user_id, 
                        old_status.value, 
                        "in_game"
                    )
                    logger.info(f"Usuario {user_id} automáticamente marcado como 'in_game' al iniciar partida")
                else:
                    logger.warning(f"No se pudo actualizar estado para usuario {user_id} al iniciar partida")
                    
        except Exception as e:
            logger.error(f"Error actualizando estados automáticos al iniciar partida: {e}")
    
    async def auto_update_status_on_player_death(self, user_id: str):
        """Actualizar automáticamente el estado a 'in_game' cuando un jugador muere"""
        try:
            # Actualizar estado de 'alive_in_game' a 'in_game' (muerto pero observando)
            status_update = UserStatusUpdate(status=UserStatus.IN_GAME)
            updated_user, old_status = update_user_status(user_id, status_update)
            
            if updated_user and old_status:
                # Notificar cambio de estado a otros usuarios
                await self.broadcast_status_change(
                    user_id, 
                    old_status.value, 
                    "in_game"
                )
                logger.info(f"Usuario {user_id} automáticamente marcado como 'in_game' (muerto) en la partida")
            else:
                logger.warning(f"No se pudo actualizar estado para usuario {user_id} al morir")
                
        except Exception as e:
            logger.error(f"Error actualizando estado automático al morir jugador {user_id}: {e}")
    
    async def broadcast_status_change(self, user_id: str, old_status: str, new_status: str, exclude_connection: str | None = None):
        """Notificar cambio de estado a todos los usuarios conectados"""
        try:
            # Crear mensaje de notificación
            status_message = UserStatusChangedMessage(
                user_id=user_id,
                old_status=old_status,
                new_status=new_status,
                message=f"Usuario {user_id} cambió su estado de '{old_status}' a '{new_status}'"
            )
            
            # Enviar a todas las conexiones activas (excluyendo la especificada)
            for conn_id, websocket in connection_manager.active_connections.items():
                if exclude_connection and conn_id == exclude_connection:
                    continue
                
                try:
                    await connection_manager.send_personal_message(conn_id, status_message)
                except Exception as e:
                    logger.warning(f"Error enviando notificación de estado a {conn_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error notificando cambio de estado: {e}")
    
    async def send_error(self, connection_id: str, error_code: str, message: str):
        """Enviar mensaje de error"""
        await connection_manager.send_personal_message(connection_id, ErrorMessage(
            error_code=error_code,
            message=message
        ))

# Instancia global del handler
user_status_handler = UserStatusHandler()

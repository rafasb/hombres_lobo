"""
Game Handlers para WebSocket
Maneja eventos específicos del juego: iniciar, unirse, fases, etc.
"""
from app.websocket.connection_manager import connection_manager
from app.websocket.messages import (
    MessageType, GameStartedMessage, PhaseChangedMessage
)
from app.services.game_state_service import game_state_manager
from app.models.game_and_roles import GameStatus
import logging

logger = logging.getLogger(__name__)

class GameHandler:
    """Manejador de eventos específicos del juego"""
    
    async def handle_join_game(self, connection_id: str, message_data: dict):
        """Manejar unión a juego"""
        try:
            # Obtener información de conexión
            conn_info = connection_manager.get_connection_info(connection_id)
            if not conn_info:
                return
            
            game_id = conn_info["game_id"]
            user_id = conn_info["user_id"]
            
            # Obtener o crear estado del juego
            game_state = await game_state_manager.get_or_create_game_state(game_id)
            if not game_state:
                await self._send_error(connection_id, "GAME_NOT_FOUND", "Juego no encontrado")
                return
            
            # Agregar jugador al estado
            game_state.add_connected_player(user_id)
            
            # Notificar estado actual del juego
            await self._send_game_status(game_id, game_state)
            
            logger.info(f"Jugador {user_id} se unió al juego {game_id}")
            
        except Exception as e:
            logger.error(f"Error en join_game: {e}")
            await self._send_error(connection_id, "JOIN_ERROR", "Error uniéndose al juego")
    
    async def handle_start_game(self, connection_id: str, message_data: dict):
        """Manejar inicio de juego"""
        try:
            conn_info = connection_manager.get_connection_info(connection_id)
            if not conn_info:
                return
            
            game_id = conn_info["game_id"]
            user_id = conn_info["user_id"]
            
            game_state = await game_state_manager.get_or_create_game_state(game_id)
            if not game_state:
                await self._send_error(connection_id, "GAME_NOT_FOUND", "Juego no encontrado")
                return
            
            # Verificar que sea el creador (por ahora saltamos esta verificación)
            # TODO: Verificar permisos de inicio
            
            # Cambiar estado a jugando
            game_state.change_phase(GameStatus.STARTED, duration_minutes=10)
            
            # Notificar inicio de juego
            start_message = GameStartedMessage(
                players=[{"id": p, "name": f"Player {p}"} for p in game_state.connected_players],
                roles_assigned=True
            )
            
            await connection_manager.broadcast_to_game(
                game_id,
                start_message.model_dump()
            )
            
            # Enviar cambio de fase
            await self._send_phase_change(game_id, game_state)
            
            logger.info(f"Juego {game_id} iniciado por {user_id}")
            
        except Exception as e:
            logger.error(f"Error en start_game: {e}")
            await self._send_error(connection_id, "START_ERROR", "Error iniciando juego")
    
    async def handle_get_game_status(self, connection_id: str, message_data: dict):
        """Obtener estado actual del juego"""
        try:
            conn_info = connection_manager.get_connection_info(connection_id)
            if not conn_info:
                return
            
            game_id = conn_info["game_id"]
            game_state = await game_state_manager.get_or_create_game_state(game_id)
            
            if game_state:
                await self._send_game_status(game_id, game_state)
            else:
                await self._send_error(connection_id, "GAME_NOT_FOUND", "Juego no encontrado")
                
        except Exception as e:
            logger.error(f"Error en get_game_status: {e}")
            await self._send_error(connection_id, "STATUS_ERROR", "Error obteniendo estado")
    
    async def _send_game_status(self, game_id: str, game_state):
        """Enviar estado del juego a todos los conectados"""
        status_message = {
            "type": MessageType.SYSTEM_MESSAGE.value,
            "message": f"Estado del juego: {game_state.phase.value}",
            "data": {
                "game_id": game_id,
                "phase": game_state.phase.value,
                "connected_players": list(game_state.connected_players),
                "living_players": game_state.get_living_players(),
                "dead_players": game_state.get_dead_players(),
                "time_remaining": game_state.get_phase_time_remaining()
            }
        }
        
        await connection_manager.broadcast_to_game(game_id, status_message)
    
    async def _send_phase_change(self, game_id: str, game_state):
        """Enviar cambio de fase"""
        phase_message = PhaseChangedMessage(
            phase=game_state.phase.value,
            duration=int(game_state.phase_duration.total_seconds())
        )
        
        await connection_manager.broadcast_to_game(
            game_id,
            phase_message.model_dump()
        )
    
    async def _send_error(self, connection_id: str, error_code: str, message: str):
        """Enviar mensaje de error"""
        error_message = {
            "type": MessageType.ERROR.value,
            "error_code": error_code,
            "message": message
        }
        await connection_manager.send_personal_message(connection_id, error_message)

# Instancia global del game handler
game_handler = GameHandler()

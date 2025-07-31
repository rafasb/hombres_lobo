"""
Voting Handlers para WebSocket
Maneja eventos de votación en tiempo real
"""
from datetime import datetime
from app.websocket.connection_manager import connection_manager
from app.websocket.messages import (
    MessageType, VoteMessage, VotingResultsMessage, SystemMessage, ErrorMessage
)
from app.services.voting_service import voting_service
import logging

logger = logging.getLogger(__name__)

class VotingHandler:
    """Manejador de eventos de votación"""
    
    def __init__(self):
        # Registrar callbacks en el voting service
        voting_service.add_vote_callback(self._on_vote_cast)
        voting_service.add_result_callback(self._on_voting_finished)
    
    async def handle_cast_vote(self, connection_id: str, message_data: dict):
        """Manejar emisión de voto"""
        try:
            # Obtener información de conexión
            conn_info = connection_manager.get_connection_info(connection_id)
            if not conn_info:
                await self._send_error(connection_id, "CONNECTION_ERROR", "Información de conexión no encontrada")
                return
            
            game_id = conn_info["game_id"]
            user_id = conn_info["user_id"]
            
            # Validar datos del mensaje
            target_id = message_data.get("target_id")
            if not target_id:
                await self._send_error(connection_id, "INVALID_TARGET", "ID de objetivo requerido")
                return
            
            # Emitir voto
            success, message = await voting_service.cast_vote(game_id, user_id, target_id)
            
            if success:
                # Voto exitoso - se notificará via callback
                await self._send_success(connection_id, "VOTE_CAST", message)
            else:
                await self._send_error(connection_id, "VOTE_FAILED", message)
            
            logger.info(f"Voto procesado: {user_id} -> {target_id} en {game_id}: {message}")
            
        except Exception as e:
            logger.error(f"Error en cast_vote: {e}")
            await self._send_error(connection_id, "VOTE_ERROR", "Error procesando voto")
    
    async def handle_get_voting_status(self, connection_id: str, message_data: dict):
        """Obtener estado actual de votación"""
        try:
            conn_info = connection_manager.get_connection_info(connection_id)
            if not conn_info:
                await self._send_error(connection_id, "CONNECTION_ERROR", "Información de conexión no encontrada")
                return
            
            game_id = conn_info["game_id"]
            status = voting_service.get_voting_status(game_id)
            
            # Enviar estado de votación
            await connection_manager.send_personal_message(
                connection_id,
                {
                    "type": MessageType.SUCCESS,
                    "action": "voting_status",
                    "data": status,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Error en get_voting_status: {e}")
            await self._send_error(connection_id, "STATUS_ERROR", "Error obteniendo estado de votación")
    
    async def _on_vote_cast(self, game_id: str, voter_id: str, target_id: str, old_vote):
        """Callback cuando se emite un voto"""
        try:
            # Crear mensaje de voto
            vote_message = VoteMessage(
                voter_id=voter_id,
                target_id=target_id,
                vote_type="day_vote"
            )
            
            # Broadcast a todos en el juego
            await connection_manager.broadcast_to_game(
                game_id,
                vote_message.model_dump(mode='json')
            )
            
            # También enviar estado actualizado
            status = voting_service.get_voting_status(game_id)
            await connection_manager.broadcast_to_game(
                game_id,
                {
                    "type": MessageType.VOTING_STARTED,  # Reutilizamos para updates
                    "voting_status": status,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Error en callback de voto: {e}")
    
    async def _on_voting_finished(self, game_id: str, session):
        """Callback cuando termina una votación"""
        try:
            # Crear mensaje de resultados
            vote_counts = session.get_vote_counts()
            
            results_message = VotingResultsMessage(
                vote_type=session.vote_type.value,
                results=vote_counts,
                eliminated_player=session.result,
                is_tie=session.is_tie
            )
            
            # Broadcast resultados
            await connection_manager.broadcast_to_game(
                game_id,
                results_message.model_dump(mode='json')
            )
            
            # Mensaje del sistema con resultado
            if session.result:
                system_message = SystemMessage(
                    message=f"Jugador eliminado por votación: {session.result}",
                    message_key="player_eliminated_by_vote",
                    params={"player_id": session.result, "vote_counts": vote_counts}
                )
            else:
                system_message = SystemMessage(
                    message="Votación terminó en empate",
                    message_key="voting_tie",
                    params={"tied_players": [p for p, v in session.get_leading_candidates() if v == session.get_leading_candidates()[0][1]]}
                )
            
            await connection_manager.broadcast_to_game(
                game_id,
                system_message.model_dump(mode='json')
            )
            
        except Exception as e:
            logger.error(f"Error en callback de resultado: {e}")
    
    async def _send_error(self, connection_id: str, error_code: str, message: str):
        """Enviar mensaje de error"""
        error_message = ErrorMessage(
            error_code=error_code,
            message=message
        )
        await connection_manager.send_personal_message(
            connection_id,
            error_message.model_dump(mode='json')
        )
    
    async def _send_success(self, connection_id: str, action: str, message: str):
        """Enviar mensaje de éxito"""
        from app.websocket.messages import SuccessMessage
        success_message = SuccessMessage(
            action=action,
            message=message
        )
        await connection_manager.send_personal_message(
            connection_id,
            success_message.model_dump(mode='json')
        )

# Instancia global del handler de votaciones
voting_handler = VotingHandler()

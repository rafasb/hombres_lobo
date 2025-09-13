"""
Game Handlers para WebSocket
Maneja eventos específicos del juego: iniciar, unirse, fases, etc.
"""
from app.websocket.connection_manager import connection_manager
from app.websocket.messages_types import (
    MessageType, WsMessageError,ErrorCode, WsPhaseChangedMessage,
    WsTimerMessage, WsVotingStartedMessage, WsMessageGameStatus,
)
from app.websocket.user_status_handlers import user_status_handler
from app.services.game_state_service import game_state_manager, GameState
from app.services.game_phases_service import GamePhase
from app.services.voting_service import voting_service, VoteType
from app.services.game_service import get_game
from app.services.user_service import UserService
import logging

logger = logging.getLogger(__name__)

class GameHandler:
    """Manejador de eventos específicos del juego"""
    
    async def _auto_start_game(self, game_id: str, game_state: GameState):
        """Iniciar juego automáticamente cuando se alcanza el máximo de jugadores"""
        try:
            logger.info(f"Iniciando juego automáticamente: {game_id}")
            
            # Iniciar sistema de fases integrado
            await game_state.start_game_phases()
            
            # Actualizar estado de todos los jugadores a 'alive_in_game'
            try:
                
                connected_player_ids = list(game_state.connected_players)
                await user_status_handler.auto_update_status_on_game_start(connected_player_ids)
            except Exception as e:
                logger.warning(f"Error actualizando estados de jugadores al auto-iniciar juego: {e}")
            
            # Configurar callbacks para eventos de fase
            game_state.phase_controller.add_phase_change_callback(
                lambda old_phase, new_phase: self._on_phase_changed(game_id, old_phase, new_phase)
            )
            
            game_state.phase_controller.add_phase_timer_callback(
                lambda phase, time_remaining: self._on_phase_timer(game_id, phase, time_remaining)
            )

            players_info = game_state.player_states

            # Notificar inicio automático de juego
            start_message = WsMessageGameStatus(
                type=MessageType.GAME_STARTED,
                game_id=game_id,
                phase=game_state.phase_controller.current_phase if game_state.phase_controller else GamePhase.WAITING,
                players=players_info,  # Se puede llenar si es necesario
                connected_players=list(game_state.connected_players),
                living_players=game_state.get_living_players(),
                dead_players=game_state.get_dead_players(),
                is_first_night=game_state.is_first_night,
                time_remaining=game_state.get_phase_time_remaining()
            )
            
            await connection_manager.broadcast_to_game(
                game_id,
                start_message
            )
            
            logger.info(f"Juego {game_id} iniciado automáticamente")
            
        except Exception as e:
            logger.error(f"Error en auto-inicio del juego {game_id}: {e}")
            # Notificar error a todos los jugadores
            error_notification = WsMessageError(
                data="Error al iniciar el juego automáticamente. Puedes intentar iniciarlo manualmente."
            )
            await connection_manager.broadcast_to_game(game_id, error_notification)
        
    async def _on_phase_changed(self, game_id: str, old_phase: GamePhase, new_phase: GamePhase):
        """Callback cuando cambia la fase del juego"""
        try:
            # Obtener información de fase
            game_state = await game_state_manager.get_or_create_game_state(game_id)
            if not game_state:
                return
                
            phase_info = game_state.phase_controller.get_phase_info()
            
            # Crear mensaje de cambio de fase
            phase_message = WsPhaseChangedMessage(
                data=new_phase.value,
                duration=phase_info["duration"]
            )
            
            # Broadcast a todos los jugadores
            await connection_manager.broadcast_to_game(
                game_id,
                phase_message
            )
            
            # *** INTEGRACIÓN CON SISTEMA DE VOTACIONES ***
            # Si entramos en fase de VOTING, iniciar votación automáticamente
            if new_phase == GamePhase.VOTING:
                await self._start_day_voting(game_id, game_state)
            
            logger.info(f"Juego {game_id}: Fase cambiada de {old_phase.value} a {new_phase.value}")
            
        except Exception as e:
            logger.error(f"Error en callback de cambio de fase: {e}")
    
    async def _start_day_voting(self, game_id: str, game_state):
        """Iniciar votación diurna automáticamente"""
        try:
            # Obtener jugadores vivos (por ahora todos los conectados)
            eligible_voters = list(game_state.connected_players)
            vote_targets = list(game_state.connected_players)
            
            # Crear sesión de votación
            await voting_service.create_voting_session(
                game_id=game_id,
                vote_type=VoteType.DAY_VOTE,
                eligible_voters=eligible_voters,
                vote_targets=vote_targets,
                duration_seconds=120  # 2 minutos
            )
            
            # Iniciar votación
            success = await voting_service.start_voting_session(game_id)
            
            if success:
                # Notificar inicio de votación
                voting_message = WsVotingStartedMessage(
                    data=VoteType.DAY_VOTE,
                    duration=120,
                    type=MessageType.VOTING_STARTED,
                    game_id=game_id,
                    eligible_voters=eligible_voters,
                    vote_targets=vote_targets
                )
                
                await connection_manager.broadcast_to_game(game_id, voting_message)
                logger.info(f"Votación diurna iniciada para juego {game_id}")
            else:
                logger.error(f"Error iniciando votación para juego {game_id}")
                
        except Exception as e:
            logger.error(f"Error iniciando votación diurna: {e}")
    
    async def _on_phase_timer(self, game_id: str, phase: GamePhase, time_remaining: int):
        """Callback para updates de timer de fase"""
        try:
            # Enviar update de timer a todos los jugadores
            timer_message = WsTimerMessage(
                phase=phase.value,
                data=time_remaining,
                game_id=game_id
            )
            
            await connection_manager.broadcast_to_game(game_id, timer_message)
            
        except Exception as e:
            logger.error(f"Error en callback de timer: {e}")
        
    async def _send_game_status(self, game_id: str, game_state: GameState):
        """Enviar estado del juego a todos los conectados"""
        
        status_message = self.build_game_status_message(game_id, game_state)
        # TODO: Cambiar a WebSocketMessageGameStatus si es posible

        await connection_manager.broadcast_to_game(game_id, status_message)

    def build_game_status_message(self, game_id: str, game_state: GameState) -> WsMessageGameStatus:
        """Construir y devolver el dict con el estado del juego (sin enviarlo).

        Útil para enviar el estado sólo al cliente recién conectado.
        """
        from app.database import load_user

        players_info = []
        if game_state.game_data and game_state.game_data.players:
            for player_id in game_state.game_data.players:
                user = load_user(player_id)
                if user:
                    players_info.append({
                        "id": user.id,
                        "name": user.username,
                        "is_alive": player_id not in game_state.eliminated_players,
                        "is_connected": player_id in game_state.connected_players,
                        "role": game_state.game_data.players[player_id].role if player_id in game_state.game_data.players else None
                    })

        status_message = {
            "type": MessageType.GAME_STATUS.value,
            "message": f"Estado del juego: {game_state.phase.value}",
            "data": {
                "game_id": game_id,
                "phase": game_state.phase.value,
                "players": players_info,
                "connected_players": list(game_state.connected_players),
                "living_players": game_state.get_living_players(),
                "dead_players": game_state.get_dead_players(),
                "time_remaining": game_state.get_phase_time_remaining()
            }
        }
        status_message = WsMessageGameStatus(
            game_id=game_id,
            phase=game_state.phase_controller.current_phase if game_state.phase_controller else GamePhase.WAITING,
            players=players_info,
            connected_players=list(game_state.connected_players),
            living_players=game_state.get_living_players(),
            dead_players=game_state.get_dead_players(),
            is_first_night=game_state.is_first_night,
            time_remaining=game_state.get_phase_time_remaining()
        )

        return status_message
    
    async def _send_phase_change(self, game_id: str, game_state: GameState):
        """Enviar cambio de fase"""
        phase_message = WsPhaseChangedMessage(
            data=game_state.phase.value,
            duration=int(game_state.phase_duration.total_seconds())
        )
        
        await connection_manager.broadcast_to_game(
            game_id,
            phase_message
        )
    
    async def _check_admin_permissions(self, user_id: str, game_id: str) -> bool:
        """Verificar si el usuario tiene permisos de admin para el juego"""
        try:
            # Obtener información del juego desde la base de datos
            game_info = get_game(game_id)
            if not game_info:
                return False
            
            # El creador del juego siempre tiene permisos de admin
            if game_info.creator_id == user_id:
                return True
            
            # Verificar si el usuario tiene rol de admin en el estado del juego
            game_state = await game_state_manager.get_or_create_game_state(game_id)
            if game_state and game_state.game_data:
                # Buscar el rol del usuario
                isAdmin = UserService.is_user_admin(user_id)
                if isAdmin or game_info.creator_id == user_id:
                    return True
            
            # Por ahora, permitir al creador en cualquier caso
            return game_info.creator_id == user_id
            
        except Exception as e:
            logger.error(f"Error verificando permisos de admin: {e}")
            return False

    async def _send_error(self, connection_id: str, error_code: ErrorCode, message: str):
        """Enviar mensaje de error"""
        error_message = WsMessageError(
            error_code=error_code,
            data=message
        )
        await connection_manager.send_personal_message(connection_id, error_message)

# Instancia global del game handler
game_handler = GameHandler()

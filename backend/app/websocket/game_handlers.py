"""
Game Handlers para WebSocket
Maneja eventos específicos del juego: iniciar, unirse, fases, etc.
"""
from app.websocket.connection_manager import connection_manager
from app.websocket.messages import (
    MessageType, GameStartedMessage, PhaseChangedMessage
)
from app.services.game_state_service import game_state_manager, GameState
from app.services.game_phases_service import GamePhase
from app.services.voting_service import voting_service, VoteType
from app.services.game_service import join_game, get_game
from app.services.user_service import get_user
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
            
            # Verificar si el usuario está en la base de datos del juego
            user_in_game = False
            if game_state.game_data and game_state.game_data.players:
                user_in_game = user_id in game_state.game_data.players
            
            # Si no está en la base de datos, añadirlo automáticamente
            if not user_in_game:
                try:
                    # Obtener información del usuario
                    user = get_user(user_id)
                    if user:
                        # Intentar añadir el usuario al juego en la base de datos
                        result = join_game(game_id, user_id)
                        if result:
                            # Recargar el estado del juego para incluir el nuevo jugador
                            game_state = await game_state_manager.get_or_create_game_state(game_id)
                except Exception as e:
                    logger.error(f"Error añadiendo usuario {user_id} a la base de datos del juego {game_id}: {e}")
            
            # Verificar que el game_state sea válido después de posibles modificaciones
            if not game_state:
                await self._send_error(connection_id, "GAME_NOT_FOUND", "Error cargando estado del juego")
                return
            
            # Agregar jugador al estado en memoria
            game_state.add_connected_player(user_id)
            
            # Notificar solo la conexión del jugador (no enviar todo el estado aquí para evitar duplicados)
            await connection_manager.broadcast_to_game(game_id, {
                "type": "player_connected",
                "user_id": user_id
            }, exclude_connection=None)
            
            # *** NUEVA LÓGICA: Verificar si se alcanzó el número máximo de jugadores para auto-inicio ***
            if game_state.game_data and game_state.game_data.players:
                current_players = len(game_state.game_data.players)
                
                # Obtener información actualizada del juego desde la base de datos
                game_info = get_game(game_id)
                if not game_info:
                    logger.warning(f"No se pudo obtener información del juego {game_id} para auto-inicio")
                    return
                
                max_players = game_info.max_players
                
                logger.info(f"Juego {game_id}: {current_players}/{max_players} jugadores")
                
                # Si se alcanzó el máximo de jugadores y el juego está en estado WAITING, iniciarlo automáticamente
                if (current_players >= max_players and 
                    game_state.game_data.status.value == "waiting" and
                    not (game_state.phase_controller and game_state.phase_controller.is_active)):
                    
                    logger.info(f"Auto-iniciando juego {game_id} - Máximo de jugadores alcanzado ({current_players}/{max_players})")
                    
                    try:
                        # Iniciar el juego automáticamente
                        await self._auto_start_game(game_id, game_state)
                    except Exception as e:
                        logger.error(f"Error en auto-inicio del juego {game_id}: {e}")
            
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
            
            # Iniciar sistema de fases integrado
            await game_state.start_game_phases()
            
            # Actualizar estado de todos los jugadores a 'alive_in_game'
            try:
                from app.websocket.user_status_handlers import user_status_handler
                connected_player_ids = list(game_state.connected_players)
                await user_status_handler.auto_update_status_on_game_start(connected_player_ids)
            except Exception as e:
                logger.warning(f"Error actualizando estados de jugadores al iniciar juego: {e}")
            
            # Configurar callbacks para eventos de fase
            game_state.phase_controller.add_phase_change_callback(
                lambda old_phase, new_phase: self._on_phase_changed(game_id, old_phase, new_phase)
            )
            
            game_state.phase_controller.add_phase_timer_callback(
                lambda phase, time_remaining: self._on_phase_timer(game_id, phase, time_remaining)
            )
            
            # Notificar inicio de juego
            start_message = GameStartedMessage(
                players=[{"id": p, "name": f"Player {p}"} for p in game_state.connected_players],
                roles_assigned=True
            )
            
            await connection_manager.broadcast_to_game(
                game_id,
                start_message
            )
            
            logger.info(f"Juego {game_id} iniciado por {user_id}")
            
        except Exception as e:
            logger.error(f"Error en start_game: {e}")
            await self._send_error(connection_id, "START_ERROR", "Error iniciando juego")
    
    async def _auto_start_game(self, game_id: str, game_state: GameState):
        """Iniciar juego automáticamente cuando se alcanza el máximo de jugadores"""
        try:
            logger.info(f"Iniciando juego automáticamente: {game_id}")
            
            # Iniciar sistema de fases integrado
            await game_state.start_game_phases()
            
            # Actualizar estado de todos los jugadores a 'alive_in_game'
            try:
                from app.websocket.user_status_handlers import user_status_handler
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
            
            # Notificar inicio automático de juego
            start_message = GameStartedMessage(
                players=[{"id": p, "name": f"Player {p}"} for p in game_state.connected_players],
                roles_assigned=True
            )
            
            await connection_manager.broadcast_to_game(
                game_id,
                start_message
            )
            
            # Notificar que el juego se inició automáticamente
            auto_start_notification = {
                "type": "game_auto_started",
                "message": "¡El juego se ha iniciado automáticamente al completarse todos los jugadores!"
            }
            
            await connection_manager.broadcast_to_game(game_id, auto_start_notification)
            
            logger.info(f"Juego {game_id} iniciado automáticamente")
            
        except Exception as e:
            logger.error(f"Error en auto-inicio del juego {game_id}: {e}")
            # Notificar error a todos los jugadores
            error_notification = {
                "type": "auto_start_error",
                "message": "Error al iniciar el juego automáticamente. Puedes intentar iniciarlo manualmente."
            }
            await connection_manager.broadcast_to_game(game_id, error_notification)
    
    async def handle_restart_game(self, connection_id: str, message_data: dict):
        """Reiniciar partida (solo admin)"""
        try:
            conn_info = connection_manager.get_connection_info(connection_id)
            if not conn_info:
                return
            
            game_id = conn_info["game_id"]
            user_id = conn_info["user_id"]
            
            # Verificar que el usuario tenga permisos de admin
            if not await self._check_admin_permissions(user_id, game_id):
                await self._send_error(connection_id, "INSUFFICIENT_PERMISSIONS", "Solo los administradores pueden reiniciar la partida")
                return
            
            game_state = await game_state_manager.get_or_create_game_state(game_id)
            if not game_state:
                await self._send_error(connection_id, "GAME_NOT_FOUND", "Juego no encontrado")
                return
            
            logger.info(f"Admin {user_id} reiniciando juego {game_id}")
            
            # Detener sistema de fases si está activo
            if game_state.phase_controller and game_state.phase_controller.is_active:
                try:
                    # Marcar como inactivo para detener timers
                    game_state.phase_controller.is_active = False
                    logger.info(f"Sistema de fases detenido para juego {game_id}")
                except Exception as e:
                    logger.warning(f"Error deteniendo sistema de fases: {e}")
            
            # Detener votaciones activas - simplificado
            try:
                # Solo registrar que se intenta detener votaciones
                logger.info(f"Deteniendo votaciones activas para juego {game_id}")
            except Exception as e:
                logger.warning(f"Error deteniendo votación al reiniciar: {e}")
            
            # Limpiar estado del juego
            game_state.eliminated_players.clear()
            
            # Notificar reinicio a todos los jugadores
            restart_message = {
                "type": "game_restarted",
                "message": "La partida ha sido reiniciada por el administrador",
                "admin": user_id
            }
            
            await connection_manager.broadcast_to_game(game_id, restart_message)
            
            # Enviar estado actualizado
            await self._send_game_status(game_id, game_state)
            
            # Confirmación al admin
            success_message = {
                "type": MessageType.SUCCESS.value,
                "action": "restart_game",
                "message": "Partida reiniciada exitosamente",
                "data": {
                    "game_id": game_id,
                    "restarted_by": user_id
                }
            }
            await connection_manager.send_personal_message(connection_id, success_message)
            
            logger.info(f"Juego {game_id} reiniciado por admin {user_id}")
            
        except Exception as e:
            logger.error(f"Error en restart_game: {e}")
            await self._send_error(connection_id, "RESTART_ERROR", "Error reiniciando la partida")

    async def handle_force_next_phase(self, connection_id: str, message_data: dict):
        """Manejar cambio forzado a la siguiente fase (solo creador)"""
        try:
            # Obtener información de conexión
            conn_info = connection_manager.get_connection_info(connection_id)
            if not conn_info:
                return
            
            game_id = conn_info["game_id"]
            user_id = conn_info["user_id"]
            
            # Obtener estado del juego
            game_state = await game_state_manager.get_or_create_game_state(game_id)
            if not game_state:
                await self._send_error(connection_id, "GAME_NOT_FOUND", "Juego no encontrado")
                return
            
            # TODO: Verificar que sea el creador del juego
            # Por ahora permitimos a todos los usuarios (para testing)
            
            # Verificar que el juego esté iniciado
            if not game_state.phase_controller or not game_state.phase_controller.is_active:
                await self._send_error(connection_id, "GAME_NOT_STARTED", "El juego no está iniciado")
                return
            
            # Obtener la siguiente fase
            current_phase = game_state.phase_controller.current_phase
            phase_config = game_state.phase_controller.phase_config.get(current_phase)
            
            if not phase_config:
                await self._send_error(connection_id, "INVALID_PHASE", "Fase actual inválida")
                return
            
            next_phase = phase_config.next_phase
            
            # Forzar cambio de fase
            success = await game_state.phase_controller.change_phase(next_phase, force=True)
            
            if success:
                # Enviar confirmación al creador
                success_message = {
                    "type": MessageType.SUCCESS.value,
                    "action": "force_next_phase",
                    "message": f"Fase cambiada manualmente de {current_phase.value} a {next_phase.value}",
                    "data": {
                        "old_phase": current_phase.value,
                        "new_phase": next_phase.value
                    }
                }
                await connection_manager.send_personal_message(connection_id, success_message)
                
                logger.info(f"Usuario {user_id} forzó cambio de fase en juego {game_id}: {current_phase.value} -> {next_phase.value}")
            else:
                await self._send_error(connection_id, "PHASE_CHANGE_FAILED", "No se pudo cambiar la fase")
                
        except Exception as e:
            logger.error(f"Error en force_next_phase: {e}")
            await self._send_error(connection_id, "FORCE_PHASE_ERROR", "Error forzando cambio de fase")
    
    async def _on_phase_changed(self, game_id: str, old_phase: GamePhase, new_phase: GamePhase):
        """Callback cuando cambia la fase del juego"""
        try:
            # Obtener información de fase
            game_state = await game_state_manager.get_or_create_game_state(game_id)
            if not game_state:
                return
                
            phase_info = game_state.phase_controller.get_phase_info()
            
            # Crear mensaje de cambio de fase
            phase_message = PhaseChangedMessage(
                phase=new_phase.value,
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
                voting_message = {
                    "type": MessageType.VOTING_STARTED.value,
                    "vote_type": "day_vote",
                    "duration": 120,
                    "eligible_voters": eligible_voters,
                    "vote_targets": vote_targets,
                    "game_id": game_id
                }
                
                await connection_manager.broadcast_to_game(game_id, voting_message)
                logger.info(f"Votación diurna iniciada para juego {game_id}")
            else:
                logger.error(f"Error iniciando votación para juego {game_id}")
                
        except Exception as e:
            logger.error(f"Error iniciando votación diurna: {e}")
    
    async def _on_phase_timer(self, game_id: str, phase: GamePhase, time_remaining: int):
        """Callback para updates de timer de fase"""
        try:
            # Enviar update de timer
            timer_message = {
                "type": MessageType.PHASE_TIMER.value,
                "phase": phase.value,
                "time_remaining": time_remaining,
                "game_id": game_id
            }
            
            await connection_manager.broadcast_to_game(game_id, timer_message)
            
        except Exception as e:
            logger.error(f"Error en callback de timer: {e}")
    
    async def handle_get_game_status(self, connection_id: str, message_data: dict):
        """Obtener estado actual del juego"""
        try:
            conn_info = connection_manager.get_connection_info(connection_id)
            if not conn_info:
                return
            
            game_id = conn_info["game_id"]
            game_state = await game_state_manager.get_or_create_game_state(game_id)
            
            if game_state:
                # Enviar el estado únicamente al solicitante para evitar duplicados
                status_msg = self.build_game_status_message(game_id, game_state)
                await connection_manager.send_personal_message(connection_id, status_msg)
            else:
                await self._send_error(connection_id, "GAME_NOT_FOUND", "Juego no encontrado")
                
        except Exception as e:
            logger.error(f"Error en get_game_status: {e}")
            await self._send_error(connection_id, "STATUS_ERROR", "Error obteniendo estado")
    
    async def _send_game_status(self, game_id: str, game_state):
        """Enviar estado del juego a todos los conectados"""
        from app.database import load_user
        
        # Obtener información completa de jugadores
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
                        "role": game_state.game_data.roles.get(player_id, {}).get("role") if game_state.game_data.roles else None
                    })
        
        status_message = {
            "type": MessageType.SYSTEM_MESSAGE.value,
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

        await connection_manager.broadcast_to_game(game_id, status_message)

    def build_game_status_message(self, game_id: str, game_state) -> dict:
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
                        "role": game_state.game_data.roles.get(player_id, {}).get("role") if game_state.game_data.roles else None
                    })

        status_message = {
            "type": MessageType.SYSTEM_MESSAGE.value,
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

        return status_message
    
    async def _send_phase_change(self, game_id: str, game_state):
        """Enviar cambio de fase"""
        phase_message = PhaseChangedMessage(
            phase=game_state.phase.value,
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
                if game_state.game_data.roles and user_id in game_state.game_data.roles:
                    user_role = game_state.game_data.roles[user_id]
                    # Para simplificar, también permitir que el creador sea admin
                    if user_role.role.value == "admin" or game_info.creator_id == user_id:
                        return True
            
            # Por ahora, permitir al creador en cualquier caso
            return game_info.creator_id == user_id
            
        except Exception as e:
            logger.error(f"Error verificando permisos de admin: {e}")
            return False

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

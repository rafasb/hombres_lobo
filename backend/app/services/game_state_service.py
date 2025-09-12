"""
Game State Service
Maneja el estado del juego en memoria integrado con sistema de fases
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
from app.models.game_and_player import Game, GameStatus, PlayerInfo
from app.services.game_phases_service import GamePhaseController, GamePhase, phase_manager
from app.services.user_service import UserService
from app.models.user import UserStatus

class GameState:
    """Wrapper de servicios para Game - NO duplica datos.
    
    Solo mantiene estado temporal/cache y delega todas las operaciones
    de datos al modelo Game subyacente.
    """
    
    def __init__(self, game_id: str, game_data: Game):
        self.game_id = game_id
        self.game_data = game_data
        
        # Solo estado temporal que NO se debe persistir
        self.phase_controller: GamePhaseController = phase_manager.get_or_create_controller(game_id)
        self.phase_start_time = datetime.now()
        self.phase_duration = timedelta(minutes=5)
        self.phase_timer_task = None
        self.is_active = True
        
        # Sincronizar connected_players del modelo si no está inicializado
        if not hasattr(self.game_data, 'connected_players') or not self.game_data.connected_players:
            self.game_data.connected_players = []
        
        # Asegurar que eliminated_players esté sincronizado
        self._sync_eliminated_players_from_game()

    def _sync_eliminated_players_from_game(self):
        """Sincroniza eliminated_players desde el estado de los jugadores"""
        # Sincronizar eliminated_players basándose en is_alive de cada PlayerInfo
        for player_id, player_info in self.game_data.players.items():
            if not player_info.is_alive and player_id not in self.game_data.eliminated_players:
                self.game_data.eliminated_players.append(player_id)
    
    def _save_changes(self):
        """Guarda cambios en la base de datos"""
        from app.database import save_game
        save_game(self.game_data)

    # Composición helpers: delegados y propiedades convenientes
    @property
    def players(self):
        """Devuelve el diccionario de PlayerInfo del modelo Game."""
        return self.game_data.players
    
    # Retorna un array de la información de los jugadores
    @property
    def player_states(self) -> List[PlayerInfo]:
        """Devuelve la lista de PlayerInfo del modelo Game."""
        return list(self.game_data.players.values())

    @property
    def player_ids(self) -> List[str]:
        """Devuelve la lista de player_ids del modelo Game."""
        return self.game_data.player_ids
        
    @property
    def votes(self) -> Dict[str, str]:
        """Delegar al campo votes del modelo Game."""
        return self.game_data.votes
        
    @property
    def night_actions(self) -> Dict[str, Dict[str, str]]:
        """Delegar al campo night_actions del modelo Game."""
        return self.game_data.night_actions
        
    @property
    def eliminated_players(self) -> List[str]:
        """Delegar al campo eliminated_players del modelo Game."""
        return self.game_data.eliminated_players
        
    @property
    def connected_players(self) -> List[str]:
        """Delegar al campo connected_players del modelo Game."""
        return self.game_data.connected_players
        
    @property
    def is_first_night(self) -> bool:
        """Delegar al campo is_first_night del modelo Game."""
        return self.game_data.is_first_night

    def get_player_state(self, player_id: str) -> PlayerInfo | None:
        """Delegar al método get_player_state del modelo Game"""
        return self.game_data.get_player_state(player_id)
    
    def get_all_player_states(self) -> List[PlayerInfo]:
        """Delegar a la propiedad player_states del modelo Game"""
        return self.game_data.player_states

    # TODO: Cohesionar las fases y estados. Actualmente hay redundancia.
    @property
    def phase(self) -> GameStatus:
        """Obtener fase actual: usar directamente el `status` del objeto Game cuando exista.
        Mantener un fallback mínimo basado en el controlador de fases para compatibilidad.
        """
        try:
            status = getattr(self.game_data, "status", None)
            if isinstance(status, GameStatus):
                return status

            # Fallback mínimo: mapear desde GamePhase a GameStatus si `game_data.status` no está presente.
            phase_mapping = {
                GamePhase.WAITING: GameStatus.WAITING,
                GamePhase.STARTING: GameStatus.STARTING,
                GamePhase.NIGHT: GameStatus.NIGHT,
                GamePhase.DAY: GameStatus.DAY,
                GamePhase.FINISHED: GameStatus.FINISHED,
            }
            return phase_mapping.get(self.phase_controller.current_phase, GameStatus.WAITING)
        except Exception:
            return GameStatus.WAITING
    
    @property
    def current_game_phase(self) -> GamePhase:
        """Obtener fase actual del juego"""
        return self.phase_controller.current_phase
        
    def add_connected_player(self, user_id: str):
        """Delegar al método add_connected_player del modelo Game"""
        self.game_data.add_connected_player(user_id)
        self._save_changes()
        
    def remove_connected_player(self, user_id: str):
        """Delegar al método remove_connected_player del modelo Game"""
        self.game_data.remove_connected_player(user_id)
        self._save_changes()
        
    def get_living_players(self) -> List[str]:
        """Delegar al método get_living_players del modelo Game"""
        return self.game_data.get_living_players()
    
    def get_dead_players(self) -> List[str]:
        """Delegar al método get_dead_players del modelo Game"""
        return self.game_data.get_dead_players()
    
    def eliminate_player(self, user_id: str):
        """Delegar al método eliminate_player del modelo Game y persistir cambios"""
        self.game_data.eliminate_player(user_id)
        self._save_changes()
        
        # Actualizar estado del usuario automáticamente a través de WebSocket
        try:
            from app.websocket.user_status_handlers import user_status_handler
            import asyncio
            # Crear una tarea asíncrona para actualizar el estado
            asyncio.create_task(user_status_handler.auto_update_status_on_player_death(user_id))
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error actualizando estado de jugador eliminado {user_id}: {e}")
        
    def cast_vote(self, voter_id: str, target_id: str) -> bool:
        """Delegar al método cast_vote del modelo Game"""
        result = self.game_data.cast_vote(voter_id, target_id)
        if result:
            self._save_changes()
        return result
    
    def clear_votes(self):
        """Delegar al método clear_votes del modelo Game"""
        self.game_data.clear_votes()
        self._save_changes()
        
    def get_vote_count(self) -> Dict[str, int]:
        """Delegar al método get_vote_count del modelo Game"""
        return self.game_data.get_vote_count()
    
    def get_most_voted(self) -> str | None:
        """Delegar al método get_most_voted del modelo Game"""
        return self.game_data.get_most_voted()
    
    def set_night_action(self, player_id: str, action_data: dict):
        """Registrar acción nocturna en el modelo Game"""
        self.game_data.night_actions[player_id] = action_data
        self._save_changes()
        
    def clear_night_actions(self):
        """Limpiar acciones nocturnas del modelo Game"""
        self.game_data.night_actions.clear()
        self._save_changes()
        
    def change_phase(self, new_phase: GameStatus, duration_minutes: int = 5):
        """Cambiar fase del juego y persistir cambios"""
        # Verificar si estamos saliendo de la fase de noche
        if self.phase == GameStatus.NIGHT and new_phase != GameStatus.NIGHT:
            self.game_data.is_first_night = False
            self._save_changes()
        
        # Actualizar el status del game_data
        self.game_data.status = new_phase
        self._save_changes()
        
        # Convertir GameStatus a GamePhase
        status_to_phase = {
            GameStatus.WAITING: GamePhase.WAITING,
            GameStatus.STARTED: GamePhase.STARTING,
            GameStatus.NIGHT: GamePhase.NIGHT,
            GameStatus.DAY: GamePhase.DAY,
            GameStatus.PAUSED: GamePhase.DAY,  # Mapear paused a day por ahora
            GameStatus.FINISHED: GamePhase.FINISHED
        }
        
        game_phase = status_to_phase.get(new_phase, GamePhase.WAITING)
        
        # Usar el controlador de fases
        import asyncio
        asyncio.create_task(self.phase_controller.change_phase(game_phase, force=True))
        
        # Actualizar valores legacy para compatibilidad
        self.phase_start_time = datetime.now()
        self.phase_duration = timedelta(minutes=duration_minutes)
    
    async def start_game_phases(self):
        """Iniciar el sistema de fases para el juego"""
        await self.phase_controller.start_game()
    
    def get_phase_time_remaining(self) -> int:
        """Obtener tiempo restante de la fase en segundos"""
        return self.phase_controller.get_time_remaining()
    
    def is_phase_expired(self) -> bool:
        """Verificar si la fase ha expirado"""
        return self.get_phase_time_remaining() <= 0

class GameStateManager:
    """Manager para estados de juegos activos"""
    
    def __init__(self):
        self.active_games: Dict[str, GameState] = {}
        self.cleanup_task = None
        
    async def start_manager(self):
        """Iniciar el manager"""
        if not self.cleanup_task:
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def stop_manager(self):
        """Detener el manager"""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            self.cleanup_task = None
    
    async def get_or_create_game_state(self, game_id: str) -> GameState | None:
        """Obtener o crear estado de juego"""
        if game_id in self.active_games:
            return self.active_games[game_id]
        
        # Cargar juego desde base de datos
        from app.services.game_service import get_game
        
        game_data = get_game(game_id)
        
        if not game_data:
            # Si no existe en BD, crear uno básico para desarrollo
            game_data = Game(
                id=game_id,
                name=f"Juego {game_id}",
                creator_id="temp",
                max_players=10,
                player_ids=[],        # inicializar lista de ids
                players={},           # inicializar dict de PlayerInfo
                status=GameStatus.WAITING
            )
        
        # Crear nuevo estado
        game_state = GameState(game_id, game_data)
        self.active_games[game_id] = game_state
        
        return game_state
    
    async def remove_game_state(self, game_id: str):
        """Remover estado de juego"""
        if game_id in self.active_games:
            game_state = self.active_games[game_id]
            game_state.is_active = False
            
            # Cancelar timer de fase
            if game_state.phase_timer_task:
                game_state.phase_timer_task.cancel()
            
            del self.active_games[game_id]
    
    def get_active_games(self) -> List[str]:
        """Obtener lista de juegos activos"""
        return list(self.active_games.keys())
    
    async def update_connected_players(self, user_id: str, connected: bool, game_id: Optional[str] = None):
        """
        Actualizar el estado de conexión de un jugador específico
        
        Args:
            user_id: ID del usuario
            connected: True para agregar, False para eliminar de connected_players
            game_id: ID del juego específico. Si es None, busca en todos los juegos activos
        """
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            # Si se proporciona game_id específico, actualizar solo ese juego
            if game_id:
                game_state = self.active_games.get(game_id)
                if game_state:
                    self._update_player_connection_state(game_state, user_id, connected)
                    logger.info(f"Actualizado estado de conexión para usuario {user_id} en juego {game_id}: {'conectado' if connected else 'desconectado'}")
                else:
                    logger.warning(f"Juego {game_id} no encontrado en juegos activos")
            else:
                # Buscar en todos los juegos activos donde el usuario sea jugador
                updated_games = []
                for active_game_id, game_state in self.active_games.items():
                    if user_id in game_state.game_data.players:
                        self._update_player_connection_state(game_state, user_id, connected)
                        updated_games.append(active_game_id)
                
                if updated_games:
                    logger.info(f"Actualizado estado de conexión para usuario {user_id} en juegos: {updated_games}: {'conectado' if connected else 'desconectado'}")
                else:
                    logger.info(f"Usuario {user_id} no encontrado en ningún juego activo")
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error actualizando estado de conexión del jugador {user_id}: {e}")
            print(f"[GameStateManager] Error actualizando estado de conexión del jugador {user_id}: {e}")
    
    async def update_connected_players_from_list(self, game_id: str, connected_user_ids: List[str]):
        """
        Actualiza connected_players de un juego específico con una lista completa de usuarios conectados
        
        Args:
            game_id: ID del juego
            connected_user_ids: Lista de IDs de usuarios que deberían estar conectados
        """
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            game_state = self.active_games.get(game_id)
            if not game_state:
                logger.warning(f"Juego {game_id} no encontrado en juegos activos")
                return
            
            # Actualizar la lista completa de connected_players
            game_state.game_data.connected_players = list(connected_user_ids)
            
            # Guardar cambios
            game_state._save_changes()
            
            logger.info(f"Actualizada lista completa de connected_players para juego {game_id}: {connected_user_ids}")
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error actualizando connected_players para juego {game_id}: {e}")
            print(f"[GameStateManager] Error actualizando connected_players para juego {game_id}: {e}")
    
    def _update_player_connection_state(self, game_state: 'GameState', user_id: str, connected: bool|None):
        """
        Actualiza el estado de conexión de un jugador en un juego específico
        
        Args:
            game_state: Estado del juego
            user_id: ID del usuario
            connected: True para agregar, False para eliminar, None para leer el estado actual
        """
        if connected is True:
            # Agregar usuario a connected_players si no está ya
            if user_id not in game_state.game_data.connected_players:
                game_state.game_data.connected_players.append(user_id)
        elif connected is False:
            # Eliminar usuario de connected_players si está presente
            if user_id in game_state.game_data.connected_players:
                game_state.game_data.connected_players.remove(user_id)
        elif connected is None:
            # Leer el estado actual de conexión
            user_info = UserService.get_user(user_id)
            if user_info and user_info.status == UserStatus.IN_GAME:
                game_state.game_data.connected_players.append(user_id)
            elif user_id in game_state.game_data.connected_players:
                game_state.game_data.connected_players.remove(user_id)

            return False

        # Guardar cambios
        game_state._save_changes()
    
    
    async def _cleanup_loop(self):
        """Loop de limpieza para juegos inactivos"""
        while True:
            try:
                await asyncio.sleep(300)  # Verificar cada 5 minutos
                print("🧹 Ejecutando limpieza de juegos inactivos...")
                current_time = datetime.now()
                inactive_games = []
                
                for game_id, game_state in self.active_games.items():
                    # Verificar si el juego está inactivo
                    if (not game_state.connected_players and 
                        current_time - game_state.phase_start_time > timedelta(hours=2)):
                        inactive_games.append(game_id)
                
                # Remover juegos inactivos
                for game_id in inactive_games:
                    await self.remove_game_state(game_id)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error en cleanup loop: {e}")

# Instancia global del game state manager
game_state_manager = GameStateManager()

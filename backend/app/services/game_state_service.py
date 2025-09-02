"""
Game State Service
Maneja el estado del juego en memoria integrado con sistema de fases
"""
from typing import Dict, List, Set
from datetime import datetime, timedelta
import asyncio
from app.models.game_and_player import Game, GameStatus, PlayerInfo
from app.services.game_phases_service import GamePhaseController, GamePhase, phase_manager

class GameState:
    """Estado de un juego en memoria. 
    Contiene información adicional como votos, acciones nocturnas, jugadores conectados, etc.
    Integrado con el sistema de fases.
    """
    
    def __init__(self, game_id: str, game_data: Game):
        self.game_id = game_id
        self.game_data = game_data
        self.connected_players: Set[str] = set()
        
        # Integración con sistema de fases
        self.phase_controller: GamePhaseController = phase_manager.get_or_create_controller(game_id)
        
        # Estado del juego
        self.votes: Dict[str, str] = {}  # voter_id -> target_id
        self.night_actions: Dict[str, dict] = {}  # player_id -> action_data
        self.eliminated_players: Set[str] = set()
        self.is_active = True
        
        # Legacy compatibility
        self.phase_start_time = datetime.now()
        self.phase_duration = timedelta(minutes=5)
        self.phase_timer_task = None

    # Composición helpers: delegados y propiedades convenientes
    @property
    def players(self):
        """Devuelve la lista de PlayerInfo o de entradas originales (compatibilidad)."""
        return getattr(self.game_data, 'players', []) or []

    @property
    def player_ids(self) -> List[str]:
        """Devuelve la lista de player_id extraídos de `players` (soporta PlayerInfo o strings)."""
        ids: List[str] = []
        for p in self.players:
            if isinstance(p, str):
                ids.append(p)
            else:
                pid = getattr(p, 'player_id', None) or (p.get('player_id') if isinstance(p, dict) else None)
                if pid:
                    ids.append(pid)
        return ids

    def get_player_state(self, player_id: str) -> PlayerInfo | None:
        """Obtiene el PlayerInfo de un jugador específico.
        
        Args:
            player_id: ID del jugador específico
            
        Returns:
            PlayerInfo si se encuentra el jugador, None en caso contrario
        """
        try:
            player_state = self.game_data.get_player_state(player_id)
            if isinstance(player_state, PlayerInfo):
                return self.game_data.get_player_state(player_id)
            return None
        except Exception:
            # Fallback: acceder directamente al diccionario players
            players_dict = getattr(self.game_data, 'players', {})
            return players_dict.get(player_id) if isinstance(players_dict, dict) else None
    
    def get_all_player_states(self) -> List[PlayerInfo]:
        """Obtiene todos los PlayerInfos del juego.
        
        Returns:
            Lista de todos los PlayerInfos en el juego
        """
        try:
            return self.game_data.player_states
        except Exception:
            # Fallback: acceder directamente al diccionario players
            players_dict = getattr(self.game_data, 'players', {})
            return list(players_dict.values()) if isinstance(players_dict, dict) else []

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
        """Agregar jugador conectado"""
        self.connected_players.add(user_id)
        
    def remove_connected_player(self, user_id: str):
        """Remover jugador conectado"""
        self.connected_players.discard(user_id)
        
    def get_living_players(self) -> List[str]:
        """Obtener jugadores vivos"""
        if not self.players:
            return []
        return [pid for pid in self.player_ids if pid not in self.eliminated_players]
    
    def get_dead_players(self) -> List[str]:
        """Obtener jugadores muertos"""
        if not self.players:
            return []
        return [pid for pid in self.player_ids if pid in self.eliminated_players]
    
    def eliminate_player(self, user_id: str):
        """Eliminar jugador del juego y actualizar su estado"""
        self.eliminated_players.add(user_id)
        
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
        """Registrar voto de jugador"""
        if voter_id in self.get_living_players():
            self.votes[voter_id] = target_id
            return True
        return False
    
    def clear_votes(self):
        """Limpiar todos los votos"""
        self.votes.clear()
        
    def get_vote_count(self) -> Dict[str, int]:
        """Obtener conteo de votos"""
        vote_count = {}
        for target_id in self.votes.values():
            vote_count[target_id] = vote_count.get(target_id, 0) + 1
        return vote_count
    
    def get_most_voted(self) -> str | None:
        """Obtener jugador con más votos"""
        vote_count = self.get_vote_count()
        if not vote_count:
            return None
        
        max_votes = max(vote_count.values())
        most_voted = [player_id for player_id, votes in vote_count.items() if votes == max_votes]
        
        # Si hay empate, devolver None
        if len(most_voted) > 1:
            return None
        
        return most_voted[0]
    
    def set_night_action(self, player_id: str, action_data: dict):
        """Registrar acción nocturna"""
        self.night_actions[player_id] = action_data
        
    def clear_night_actions(self):
        """Limpiar acciones nocturnas"""
        self.night_actions.clear()
        
    def change_phase(self, new_phase: GameStatus, duration_minutes: int = 5):
        """Cambiar fase del juego (legacy compatibility)"""
        # Convertir GameStatus a GamePhase
        status_to_phase = {
            GameStatus.WAITING: GamePhase.WAITING,
            GameStatus.STARTED: GamePhase.STARTING,
            GameStatus.NIGHT: GamePhase.NIGHT,
            GameStatus.DAY: GamePhase.DAY,
            GameStatus.PAUSED: GamePhase.PAUSED,  # Mapear paused a day por ahora
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
    
    async def _cleanup_loop(self):
        """Loop de limpieza para juegos inactivos"""
        while True:
            try:
                await asyncio.sleep(300)  # Verificar cada 5 minutos
                
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
game_state_manager = GameStateManager()

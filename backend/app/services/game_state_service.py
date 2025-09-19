"""
Game State Service - Refactorizado para usar base de datos como fuente de verdad
Aplica principios SOLID: Single Responsibility, Open/Closed, Dependency Inversion
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
from app.models.game_and_player import Game, GameStatus, PlayerInfo
from app.services.game_phases_service import GamePhaseController, GamePhase, phase_manager
# from app.services.user_service import UserService
# from app.models.user import UserStatus
import logging

logger = logging.getLogger(__name__)

class GameState:
    """
    Wrapper que usa base de datos como fuente de verdad.
    Solo mantiene cache temporal y estado de controladores no-persistentes.
    Principio: Single Responsibility - solo gestiona estado temporal
    """
    
    def __init__(self, game_id: str):
        self.game_id = game_id
        
        # Solo estado temporal que NO se debe persistir (principio SRP)
        self.phase_controller: GamePhaseController = phase_manager.get_or_create_controller(game_id)
        self.phase_timer_task = None
        self.is_active = True
        self._cache_expiry = datetime.now()
        self._cache_duration = timedelta(seconds=30)  # Cache corto
        self._cached_game_data: Optional[Game] = None
    
    @property
    def game_data(self) -> Game:
        """
        Fuente de verdad: siempre carga desde base de datos.
        Implementa cache corto solo para optimización.
        """
        now = datetime.now()
        
        # Verificar si el cache ha expirado o no existe
        if (self._cached_game_data is None or 
            now > self._cache_expiry):
            
            self._cached_game_data = self._load_fresh_from_database()
            self._cache_expiry = now + self._cache_duration
            logger.debug(f"Recargado game_data desde DB para {self.game_id}")
        
        return self._cached_game_data
    
    def _load_fresh_from_database(self) -> Game:
        """Carga datos frescos desde base de datos"""
        from app.database import load_game
        
        game = load_game(self.game_id)
        if not game:
            # Si no existe en DB, crear uno básico
            logger.warning(f"Juego {self.game_id} no encontrado en DB, creando básico")
            game = Game(
                id=self.game_id,
                creator_id="temp",
                player_ids=[],
                name=f"Juego {self.game_id}",
                max_players=10,
                players={},
                status=GameStatus.WAITING
            )
            self._save_to_database(game)
        
        return game
    
    def _save_to_database(self, game_data: Game):
        """
        Guarda cambios INMEDIATAMENTE en la base de datos.
        Principio: Dependency Inversion - delega a capa de persistencia
        """
        from app.database import save_game
        
        if game_data is None:
            game_data = self.game_data
        
        save_game(game_data)
        
        # Invalidar cache después de guardar
        self._cached_game_data = None
        logger.debug(f"Guardado y cache invalidado para {self.game_id}")
    
    def _invalidate_cache(self):
        """Invalida el cache para forzar recarga desde DB"""
        self._cached_game_data = None
        self._cache_expiry = datetime.now() - timedelta(seconds=1)

    # Propiedades delegadas CON persistencia automática
    @property
    def players(self) -> Dict[str, PlayerInfo]:
        return self.game_data.players
    
    @property
    def player_ids(self) -> List[str]:
        return self.game_data.player_ids
    
    @property
    def connected_players(self) -> List[str]:
        return self.game_data.connected_players
    
    def add_connected_player(self, user_id: str):
        """Modifica y persiste inmediatamente"""
        game = self.game_data  # Cargar fresh data
        game.add_connected_player(user_id)
        self._save_to_database(game)
        
    def remove_connected_player(self, user_id: str):
        """Modifica y persiste inmediatamente"""
        game = self.game_data  # Cargar fresh data
        game.remove_connected_player(user_id)
        self._save_to_database(game)
    
    def cast_vote(self, voter_id: str, target_id: str) -> bool:
        """Modifica y persiste inmediatamente"""
        game = self.game_data  # Cargar fresh data
        result = game.cast_vote(voter_id, target_id)
        if result:
            self._save_to_database(game)
        return result
    
    def defeat_player(self, user_id: str):
        """Modifica y persiste inmediatamente"""
        game = self.game_data  # Cargar fresh data
        game.defeat_player(user_id)
        self._save_to_database(game)
    
    def change_phase(self, new_phase: GameStatus, duration_minutes: int = 5):
        """Modifica y persiste inmediatamente"""
        game = self.game_data  # Cargar fresh data
        
        # Verificar si estamos saliendo de la fase de noche
        if game.status == GameStatus.NIGHT and new_phase != GameStatus.NIGHT:
            game.is_first_night = False
        
        game.status = new_phase
        self._save_to_database(game)
        
        # Actualizar controlador de fases (no persistente)
        status_to_phase = {
            GameStatus.WAITING: GamePhase.WAITING,
            GameStatus.STARTED: GamePhase.STARTING,
            GameStatus.NIGHT: GamePhase.NIGHT,
            GameStatus.DAY: GamePhase.DAY,
            GameStatus.PAUSED: GamePhase.DAY,
            GameStatus.FINISHED: GamePhase.FINISHED
        }
        
        game_phase = status_to_phase.get(new_phase, GamePhase.WAITING)
        asyncio.create_task(self.phase_controller.change_phase(game_phase, force=True))


class GameStateManager:
    """
    Manager que coordina estados pero SIEMPRE usa base de datos como fuente de verdad.
    Principio: Single Responsibility - solo gestiona coordinación entre componentes
    """
    
    def __init__(self):
        # Solo cache de controladores temporales, NO datos de juego
        self.active_game_states: Dict[str, GameState] = {}
        self.cleanup_task = None
    
    async def get_or_create_game_state(self, game_id: str) -> GameState | None:
        """
        Obtiene o crea GameState controller (no datos de juego).
        Los datos siempre vienen de base de datos.
        """
        try:
            # Solo crear el controlador si no existe
            if game_id not in self.active_game_states:
                logger.info(f"Creando nuevo GameState controller para {game_id}")
                self.active_game_states[game_id] = GameState(game_id)
            
            return self.active_game_states[game_id]
            
        except Exception as e:
            logger.error(f"Error obteniendo GameState para {game_id}: {e}")
            return None
    
    async def sync_connected_players_with_connection_manager(self, game_id: str, actual_connected_users: List[str]):
        """
        Sincroniza directamente con base de datos, no con cache.
        Principio: Dependency Inversion - delega a capa de persistencia
        """
        try:
            from app.database import load_game, save_game
            
            # Cargar fresh data desde DB
            game = load_game(game_id)
            if not game:
                logger.error(f"Juego {game_id} no encontrado en DB para sincronizar")
                return
            
            # Actualizar y guardar inmediatamente
            game.connected_players = list(actual_connected_users)
            save_game(game)
            
            # Invalidar cache si existe el GameState
            if game_id in self.active_game_states:
                self.active_game_states[game_id]._invalidate_cache()
            
            logger.info(f"Sincronizados connected_players en DB para {game_id}: {actual_connected_users}")
            
            # Notificar cambios
            await self._notify_game_state_updated(game_id)
            
        except Exception as e:
            logger.error(f"Error sincronizando connected_players para {game_id}: {e}")
    
    async def update_connected_players(self, user_id: str, connected: bool, game_id: Optional[str] = None):
        """
        Actualiza directamente en base de datos, no en cache.
        """
        try:
            from app.database import load_game, save_game, find_games_by_player_id
            
            games_to_update = []
            
            if game_id:
                # Actualizar juego específico
                game = load_game(game_id)
                if game and user_id in game.players:
                    games_to_update.append(game)
            else:
                # Buscar todos los juegos donde participa el usuario
                games_to_update = find_games_by_player_id(user_id)
            
            # Actualizar cada juego en DB
            for game in games_to_update:
                if connected:
                    game.add_connected_player(user_id)
                else:
                    game.remove_connected_player(user_id)
                
                save_game(game)
                
                # Invalidar cache si existe
                if game.id in self.active_game_states:
                    self.active_game_states[game.id]._invalidate_cache()
                
                # Notificar cambios
                await self._notify_game_state_updated(game.id)
            
            logger.info(f"Actualizado estado de conexión para {user_id} en {len(games_to_update)} juegos")
            
        except Exception as e:
            logger.error(f"Error actualizando estado de conexión para {user_id}: {e}")
    
    def _find_user_games_in_database(self, user_id: str) -> List[Game]:
        """Busca juegos donde participa el usuario directamente en DB"""
        from app.database import load_all_games
        
        all_games = load_all_games()
        user_games = []
        
        for game in all_games:
            if user_id in game.players:
                user_games.append(game)
        
        return user_games
    
    async def _notify_game_state_updated(self, game_id: str):
        """Notifica cambios usando datos frescos de DB"""
        try:
            from app.websocket.connection_manager import connection_manager
            from app.services.game_responses_service import GameResponsesService
            from app.websocket.messages_types import MessageType, WebSocketMessageV2
            
            # Usar datos frescos de DB para la notificación
            game_update = GameResponsesService.create_connection_update(game_id, True)
            
            if game_update:
                update_message = WebSocketMessageV2(
                    type=MessageType.GAME_STATUS,
                    data=game_update.dict(),
                    timestamp=datetime.now()
                )
                
                await connection_manager.broadcast_to_game(game_id, update_message)
                logger.info(f"Notificación de estado enviada para {game_id}")
            
        except Exception as e:
            logger.error(f"Error notificando actualización para {game_id}: {e}")
    
    async def remove_game_state(self, game_id: str):
        """Remueve solo el controlador, los datos persisten en DB"""
        if game_id in self.active_game_states:
            game_state = self.active_game_states[game_id]
            
            # Cancelar tareas temporales
            if game_state.phase_timer_task:
                game_state.phase_timer_task.cancel()
            
            del self.active_game_states[game_id]
            logger.info(f"Removido GameState controller para {game_id}")

# Instancia global
game_state_manager = GameStateManager()

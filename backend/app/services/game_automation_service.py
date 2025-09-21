"""
Game Automation Service

Servicio responsable de la automatización del flujo de juegos siguiendo principios SOLID.
Reemplaza la lógica de GamePhaseController sin usar asyncio timers.

Principios SOLID aplicados:
- Single Responsibility: Solo gestiona automatización de fases de juego
- Open/Closed: Extensible para nuevos tipos de automatización
- Liskov Substitution: Compatible con interfaces de automatización
- Interface Segregation: Interfaces específicas por tipo de automatización
- Dependency Inversion: Depende de abstracciones, no de implementaciones concretas

Fase 3 - Creación de servicios de reemplazo
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

from app.services.game_database_service import GameDatabaseService
from app.models.game_extended import GameExtended, GamePhase
from app.models.game_and_player import GameStatus

logger = logging.getLogger(__name__)


class GameAutomationService:
    """
    Servicio de automatización de juegos que gestiona el avance automático
    de fases y la lógica de automatización sin depender de asyncio timers.
    
    Reemplaza la funcionalidad de GamePhaseController con un enfoque
    basado en polling y verificación de estados.
    """
    
    def __init__(self):
        """Inicializa el servicio de automatización."""
        self.game_db_service = GameDatabaseService()
        self.automation_settings = {
            'night_duration_minutes': 5,
            'day_duration_minutes': 10,
            'voting_duration_minutes': 3,
            'discussion_duration_minutes': 7,
            'check_interval_seconds': 30
        }
        logger.info("GameAutomationService inicializado")
    
    def process_automation_cycle(self) -> Dict[str, Any]:
        """
        Procesa un ciclo de automatización verificando todos los juegos
        que requieren acciones automáticas.
        
        Returns:
            Dict con estadísticas del ciclo de automatización
        """
        logger.debug("Iniciando ciclo de automatización")
        
        stats = {
            'games_processed': 0,
            'phases_advanced': 0,
            'games_ended': 0,
            'errors': []
        }
        
        try:
            # Obtener juegos que necesitan procesamiento
            games_to_process = self._get_games_requiring_automation()
            stats['games_processed'] = len(games_to_process)
            
            for game in games_to_process:
                try:
                    result = self._process_game_automation(game)
                    if result.get('phase_advanced'):
                        stats['phases_advanced'] += 1
                    if result.get('game_ended'):
                        stats['games_ended'] += 1
                        
                except Exception as e:
                    error_msg = f"Error procesando juego {game.id}: {str(e)}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)
            
            logger.info(f"Ciclo de automatización completado: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error en ciclo de automatización: {str(e)}")
            stats['errors'].append(str(e))
            return stats
    
    def _get_games_requiring_automation(self) -> List[GameExtended]:
        """
        Obtiene la lista de juegos que requieren procesamiento automático.
        
        Returns:
            Lista de juegos que necesitan automatización
        """
        try:
            # Obtener juegos activos
            active_games = self.game_db_service.get_active_games()
            
            games_needing_automation = []
            current_time = datetime.utcnow()
            
            for game in active_games:
                if self._should_process_game(game, current_time):
                    games_needing_automation.append(game)
            
            return games_needing_automation
            
        except Exception as e:
            logger.error(f"Error obteniendo juegos para automatización: {str(e)}")
            return []
    
    def _should_process_game(self, game: GameExtended, current_time: datetime) -> bool:
        """
        Determina si un juego necesita procesamiento automático.
        
        Args:
            game: Juego a evaluar
            current_time: Tiempo actual
            
        Returns:
            True si el juego necesita procesamiento
        """
        # Si el juego no tiene automatización habilitada
        if not game.auto_advance_enabled:
            return False
        
        # Si no hay fase activa
        if not game.current_phase:
            return False
        
        # Si no hay timestamp de inicio de fase
        if not game.phase_start_time:
            return False
        
        # Calcular si ha pasado el tiempo suficiente
        phase_duration = self._get_phase_duration_minutes(game.current_phase)
        if phase_duration is None:
            return False
        
        elapsed_time = current_time - game.phase_start_time
        required_duration = timedelta(minutes=phase_duration)
        
        return elapsed_time >= required_duration
    
    def _get_phase_duration_minutes(self, phase: GamePhase) -> Optional[int]:
        """
        Obtiene la duración configurada para una fase específica.
        
        Args:
            phase: Fase del juego
            
        Returns:
            Duración en minutos o None si no está configurada
        """
        phase_durations = {
            GamePhase.NIGHT_ACTIONS: self.automation_settings['night_duration_minutes'],
            GamePhase.DAY_DISCUSSION: self.automation_settings['day_duration_minutes'],
            GamePhase.DAY_VOTING: self.automation_settings['voting_duration_minutes'],
        }
        
        return phase_durations.get(phase)
    
    def _process_game_automation(self, game: GameExtended) -> Dict[str, bool]:
        """
        Procesa la automatización de un juego específico.
        
        Args:
            game: Juego a procesar
            
        Returns:
            Dict con información sobre las acciones realizadas
        """
        result = {'phase_advanced': False, 'game_ended': False}
        
        try:
            logger.info(f"Procesando automatización para juego {game.id}, fase {game.current_phase}")
            
            # Verificar si el juego debe terminar
            if self._should_end_game(game):
                self._end_game(game)
                result['game_ended'] = True
                return result
            
            # Avanzar a la siguiente fase
            success = self.game_db_service.advance_phase(game.id)
            if success:
                result['phase_advanced'] = True
                logger.info(f"Fase avanzada automáticamente para juego {game.id}")
            else:
                logger.warning(f"No se pudo avanzar fase para juego {game.id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error en automatización del juego {game.id}: {str(e)}")
            raise
    
    def _should_end_game(self, game: GameExtended) -> bool:
        """
        Determina si un juego debe terminar.
        
        Args:
            game: Juego a evaluar
            
        Returns:
            True si el juego debe terminar
        """
        try:
            # Obtener jugadores vivos
            living_players = game.get_living_players()

            #TODO: obtener de game.players el subconjunto de jugadores vivos
            living_players = {pid: p for pid, p in game.players.items() if p.is_alive}
            
            # Contar jugadores por bando
            werewolves = sum(1 for p in living_players.values() if p.role.lower() in ['werewolf', 'hombre_lobo'])
            villagers = len(living_players) - werewolves
            
            # Condiciones de fin
            if werewolves == 0:
                logger.info(f"Juego {game.id} terminará: no quedan hombres lobo")
                return True
            
            if werewolves >= villagers:
                logger.info(f"Juego {game.id} terminará: hombres lobo igualan o superan a aldeanos")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verificando fin de juego {game.id}: {str(e)}")
            return False
    
    def _end_game(self, game: GameExtended) -> None:
        """
        Termina un juego y actualiza su estado.
        
        Args:
            game: Juego a terminar
        """
        try:
            # Actualizar estado del juego
            game.status = GameStatus.FINISHED
            game.auto_advance_enabled = False
            game.game_end_time = datetime.now()
            
            # Guardar cambios
            self.game_db_service.save_game_extended(game)
            
            logger.info(f"Juego {game.id} terminado automáticamente")
            
        except Exception as e:
            logger.error(f"Error terminando juego {game.id}: {str(e)}")
            raise
    
    def enable_automation(self, game_id: str, settings: Optional[Dict[str, Any]] = None) -> bool:
        """
        Habilita la automatización para un juego específico.
        
        Args:
            game_id: ID del juego
            settings: Configuración opcional de automatización
            
        Returns:
            True si se habilitó correctamente
        """
        try:
            game = self.game_db_service.get_game_extended(game_id)
            if not game:
                logger.warning(f"Juego {game_id} no encontrado para habilitar automatización")
                return False
            
            game.auto_advance_enabled = True
            if not game.phase_start_time:
                game.phase_start_time = datetime.utcnow()
            
            # Aplicar configuración personalizada si se proporciona
            if settings:
                for key, value in settings.items():
                    if key in self.automation_settings:
                        self.automation_settings[key] = value
            
            success = self.game_db_service.save_game_extended(game)
            if success:
                logger.info(f"Automatización habilitada para juego {game_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error habilitando automatización para juego {game_id}: {str(e)}")
            return False
    
    def disable_automation(self, game_id: str) -> bool:
        """
        Deshabilita la automatización para un juego específico.
        
        Args:
            game_id: ID del juego
            
        Returns:
            True si se deshabilitó correctamente
        """
        try:
            game = self.game_db_service.get_game_extended(game_id)
            if not game:
                logger.warning(f"Juego {game_id} no encontrado para deshabilitar automatización")
                return False
            
            game.auto_advance_enabled = False
            
            success = self.game_db_service.save_game_extended(game)
            if success:
                logger.info(f"Automatización deshabilitada para juego {game_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deshabilitando automatización para juego {game_id}: {str(e)}")
            return False
    
    def get_automation_status(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene el estado de automatización de un juego.
        
        Args:
            game_id: ID del juego
            
        Returns:
            Diccionario con el estado de automatización o None si no se encuentra
        """
        try:
            game = self.game_db_service.get_game_extended(game_id)
            if not game:
                return None
            
            current_time = datetime.utcnow()
            
            status = {
                'game_id': game_id,
                'auto_advance_enabled': game.auto_advance_enabled,
                'current_phase': game.current_phase.value if game.current_phase else None,
                'phase_start_time': game.phase_start_time.isoformat() if game.phase_start_time else None,
                'time_until_next_phase': None,
                'should_advance': False
            }
            
            if game.auto_advance_enabled and game.current_phase and game.phase_start_time:
                phase_duration = self._get_phase_duration_minutes(game.current_phase)
                if phase_duration:
                    elapsed = current_time - game.phase_start_time
                    required = timedelta(minutes=phase_duration)
                    
                    if elapsed >= required:
                        status['should_advance'] = True
                        status['time_until_next_phase'] = 0
                    else:
                        remaining = required - elapsed
                        status['time_until_next_phase'] = int(remaining.total_seconds())
            
            return status
            
        except Exception as e:
            logger.error(f"Error obteniendo estado de automatización para juego {game_id}: {str(e)}")
            return None
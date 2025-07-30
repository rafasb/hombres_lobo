"""
Game Phases Service
Maneja las diferentes fases del juego y sus transiciones automáticas
"""
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, Optional, Callable, Any
import asyncio
import logging

logger = logging.getLogger(__name__)

class GamePhase(Enum):
    """Fases del juego"""
    WAITING = "waiting"          # Sala de espera
    STARTING = "starting"        # Iniciando juego
    NIGHT = "night"             # Fase nocturna
    DAY = "day"                 # Fase diurna  
    VOTING = "voting"           # Votaciones
    TRIAL = "trial"             # Juicio/defensa
    EXECUTION = "execution"     # Ejecución
    FINISHED = "finished"       # Juego terminado

class PhaseConfig:
    """Configuración de una fase"""
    def __init__(self, duration_minutes: int, next_phase: GamePhase, auto_advance: bool = True):
        self.duration_minutes = duration_minutes
        self.next_phase = next_phase
        self.auto_advance = auto_advance

class GamePhaseController:
    """Controlador de fases de juego"""
    
    # Configuración por defecto de fases
    DEFAULT_PHASE_CONFIG = {
        GamePhase.WAITING: PhaseConfig(0, GamePhase.STARTING, False),  # No auto advance
        GamePhase.STARTING: PhaseConfig(1, GamePhase.NIGHT, True),     # 1 minuto para preparar
        GamePhase.NIGHT: PhaseConfig(3, GamePhase.DAY, True),          # 3 minutos fase nocturna
        GamePhase.DAY: PhaseConfig(5, GamePhase.VOTING, True),         # 5 minutos discusión
        GamePhase.VOTING: PhaseConfig(2, GamePhase.EXECUTION, True),   # 2 minutos votación
        GamePhase.TRIAL: PhaseConfig(2, GamePhase.EXECUTION, True),    # 2 minutos defensa
        GamePhase.EXECUTION: PhaseConfig(1, GamePhase.NIGHT, True),    # 1 minuto ejecución
        GamePhase.FINISHED: PhaseConfig(0, GamePhase.FINISHED, False)  # Final del juego
    }
    
    def __init__(self, game_id: str, phase_config: Optional[Dict[GamePhase, PhaseConfig]] = None):
        self.game_id = game_id
        self.current_phase = GamePhase.WAITING
        self.phase_start_time: Optional[datetime] = None
        self.phase_config = phase_config or self.DEFAULT_PHASE_CONFIG.copy()
        
        # Callbacks para eventos de fase
        self.phase_change_callbacks: list[Callable] = []
        self.phase_timer_callbacks: list[Callable] = []
        
        # Task para el timer de fase
        self.phase_timer_task: Optional[asyncio.Task] = None
        
        # Estado del juego
        self.is_active = False
        
    def add_phase_change_callback(self, callback: Callable[[GamePhase, GamePhase], Any]):
        """Agregar callback para cambio de fase"""
        self.phase_change_callbacks.append(callback)
    
    def add_phase_timer_callback(self, callback: Callable[[GamePhase, int], Any]):
        """Agregar callback para timer de fase"""
        self.phase_timer_callbacks.append(callback)
    
    async def start_game(self):
        """Iniciar el juego"""
        logger.info(f"Iniciando juego {self.game_id}")
        self.is_active = True
        await self.change_phase(GamePhase.STARTING)
    
    async def change_phase(self, new_phase: GamePhase, force: bool = False):
        """Cambiar a una nueva fase"""
        if not self.is_active and new_phase != GamePhase.STARTING:
            logger.warning(f"Intento de cambiar fase en juego inactivo: {self.game_id}")
            return False
        
        old_phase = self.current_phase
        
        # Validar transición
        if not force and not self._is_valid_transition(old_phase, new_phase):
            logger.warning(f"Transición inválida de {old_phase.value} a {new_phase.value}")
            return False
        
        # Cancelar timer anterior
        if self.phase_timer_task:
            self.phase_timer_task.cancel()
            self.phase_timer_task = None
        
        # Cambiar fase
        self.current_phase = new_phase
        self.phase_start_time = datetime.now()
        
        logger.info(f"Juego {self.game_id}: {old_phase.value} -> {new_phase.value}")
        
        # Notificar callbacks
        for callback in self.phase_change_callbacks:
            try:
                result = callback(old_phase, new_phase)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Error en callback de cambio de fase: {e}")
        
        # Iniciar timer para próxima fase
        if new_phase in self.phase_config:
            config = self.phase_config[new_phase]
            if config.auto_advance and config.duration_minutes > 0:
                self.phase_timer_task = asyncio.create_task(
                    self._start_phase_timer(new_phase, config.duration_minutes)
                )
        
        # Verificar fin del juego
        if new_phase == GamePhase.FINISHED:
            await self.end_game()
        
        return True
    
    async def _start_phase_timer(self, phase: GamePhase, duration_minutes: int):
        """Iniciar timer para una fase"""
        try:
            total_seconds = duration_minutes * 60
            
            # Enviar actualizaciones cada 10 segundos
            update_interval = 10
            
            for remaining in range(total_seconds, 0, -update_interval):
                # Notificar tiempo restante
                for callback in self.phase_timer_callbacks:
                    try:
                        result = callback(phase, remaining)
                        if asyncio.iscoroutine(result):
                            await result
                    except Exception as e:
                        logger.error(f"Error en callback de timer: {e}")
                
                # Esperar intervalo
                await asyncio.sleep(min(update_interval, remaining))
            
            # Tiempo agotado - avanzar a siguiente fase
            if self.current_phase == phase:  # Verificar que no haya cambiado mientras tanto
                config = self.phase_config[phase]
                await self.change_phase(config.next_phase)
                
        except asyncio.CancelledError:
            logger.debug(f"Timer cancelado para fase {phase.value}")
        except Exception as e:
            logger.error(f"Error en timer de fase {phase.value}: {e}")
    
    def _is_valid_transition(self, from_phase: GamePhase, to_phase: GamePhase) -> bool:
        """Verificar si una transición de fase es válida"""
        # Transiciones permitidas desde cualquier fase
        universal_transitions = {GamePhase.FINISHED}
        
        if to_phase in universal_transitions:
            return True
        
        # Transiciones específicas por fase
        valid_transitions = {
            GamePhase.WAITING: {GamePhase.STARTING},
            GamePhase.STARTING: {GamePhase.NIGHT},
            GamePhase.NIGHT: {GamePhase.DAY},
            GamePhase.DAY: {GamePhase.VOTING, GamePhase.TRIAL},
            GamePhase.VOTING: {GamePhase.TRIAL, GamePhase.EXECUTION, GamePhase.DAY},
            GamePhase.TRIAL: {GamePhase.EXECUTION, GamePhase.DAY},
            GamePhase.EXECUTION: {GamePhase.NIGHT, GamePhase.FINISHED},
            GamePhase.FINISHED: set()
        }
        
        return to_phase in valid_transitions.get(from_phase, set())
    
    def get_phase_info(self) -> Dict[str, Any]:
        """Obtener información de la fase actual"""
        if not self.phase_start_time:
            return {
                "phase": self.current_phase.value,
                "time_remaining": 0,
                "duration": 0,
                "progress": 0.0
            }
        
        config = self.phase_config.get(self.current_phase)
        if not config or config.duration_minutes == 0:
            return {
                "phase": self.current_phase.value,
                "time_remaining": 0,
                "duration": 0,
                "progress": 0.0
            }
        
        # Calcular tiempo transcurrido y restante
        elapsed = datetime.now() - self.phase_start_time
        total_duration = timedelta(minutes=config.duration_minutes)
        remaining = total_duration - elapsed
        
        if remaining.total_seconds() <= 0:
            remaining = timedelta(0)
        
        progress = min(1.0, elapsed.total_seconds() / total_duration.total_seconds())
        
        return {
            "phase": self.current_phase.value,
            "time_remaining": int(remaining.total_seconds()),
            "duration": int(total_duration.total_seconds()),
            "progress": progress
        }
    
    def get_time_remaining(self) -> int:
        """Obtener tiempo restante en segundos"""
        return self.get_phase_info()["time_remaining"]
    
    def is_phase_active(self, phase: GamePhase) -> bool:
        """Verificar si una fase específica está activa"""
        return self.current_phase == phase and self.is_active
    
    async def end_game(self):
        """Terminar el juego"""
        logger.info(f"Terminando juego {self.game_id}")
        
        self.is_active = False
        
        # Cancelar timer
        if self.phase_timer_task:
            self.phase_timer_task.cancel()
            self.phase_timer_task = None
        
        # Limpiar callbacks
        self.phase_change_callbacks.clear()
        self.phase_timer_callbacks.clear()
    
    def update_phase_config(self, phase: GamePhase, config: PhaseConfig):
        """Actualizar configuración de una fase"""
        self.phase_config[phase] = config
        logger.info(f"Configuración actualizada para fase {phase.value}: {config.duration_minutes}min")


class GamePhaseManager:
    """Gestor global de fases de juego"""
    
    def __init__(self):
        self.game_controllers: Dict[str, GamePhaseController] = {}
    
    def get_or_create_controller(self, game_id: str) -> GamePhaseController:
        """Obtener o crear controlador para un juego"""
        if game_id not in self.game_controllers:
            self.game_controllers[game_id] = GamePhaseController(game_id)
            logger.info(f"Creado controlador de fases para juego {game_id}")
        
        return self.game_controllers[game_id]
    
    def remove_controller(self, game_id: str):
        """Remover controlador de un juego"""
        if game_id in self.game_controllers:
            controller = self.game_controllers[game_id]
            asyncio.create_task(controller.end_game())
            del self.game_controllers[game_id]
            logger.info(f"Removido controlador de fases para juego {game_id}")
    
    def get_active_games(self) -> list[str]:
        """Obtener lista de juegos activos"""
        return [game_id for game_id, controller in self.game_controllers.items() if controller.is_active]


# Instancia global del gestor de fases
phase_manager = GamePhaseManager()

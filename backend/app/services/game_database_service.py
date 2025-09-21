"""
GameDatabaseService - Servicio principal para operaciones de base de datos de juego
Centraliza toda la lógica de persistencia y estado del juego usando los módulos database.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

# Usar los módulos refactorizados de database
from app.database import (
    load_game, 
    load_all_games
)
from app.models.game_and_player import GameStatus
from app.models.game_extended import GameExtended, GamePhase

logger = logging.getLogger(__name__)


class GameDatabaseService:
    """
    Servicio principal para operaciones de base de datos de juego.
    
    Este servicio reemplaza la lógica distribuida entre GameState y GamePhaseController,
    centralizando todas las operaciones de estado usando los módulos database refactorizados.
    
    Principios SOLID aplicados:
    - Single Responsibility: Solo maneja lógica de negocio de juego
    - Open/Closed: Extensible sin modificar código existente
    - Liskov Substitution: Cumple contratos esperados
    - Interface Segregation: Métodos específicos por funcionalidad
    - Dependency Inversion: Depende de abstracciones (módulos database)
    """
    
    @staticmethod
    def get_game_extended(game_id: str) -> Optional[GameExtended]:
        """
        Obtiene un juego como GameExtended para operaciones avanzadas.
        
        Args:
            game_id: ID del juego a obtener
            
        Returns:
            GameExtended o None si no existe
        """
        try:
            # Usar el módulo database refactorizado
            base_game = load_game(game_id)
            if not base_game:
                logger.warning(f"Juego {game_id} no encontrado")
                return None
            
            # Convertir a GameExtended usando el método de clase
            game_extended = GameExtended.from_game(base_game)
            logger.debug(f"Juego {game_id} obtenido como GameExtended")
            return game_extended
                
        except Exception as e:
            logger.error(f"Error obteniendo juego {game_id} como GameExtended: {e}")
            return None
    
    @staticmethod
    def update_phase(game_id: str, new_phase: GamePhase, 
                    duration_seconds: Optional[int] = None,
                    auto_advance: bool = True) -> bool:
        """
        Actualiza fase del juego y establece timer automático.
        
        Args:
            game_id: ID del juego
            new_phase: Nueva fase del juego
            duration_seconds: Duración en segundos (None = sin límite)
            auto_advance: Si debe avanzar automáticamente
            
        Returns:
            True si la actualización fue exitosa
        """
        try:
            # Obtener juego actual
            game = GameDatabaseService.get_game_extended(game_id)
            if not game:
                logger.error(f"Juego {game_id} no encontrado para actualizar fase")
                return False
            
            # Actualizar campos de fase
            game.current_phase = new_phase
            game.phase_start_time = datetime.utcnow()
            game.phase_auto_advance = auto_advance
            
            # Configurar timer automático si se especifica duración
            if duration_seconds and auto_advance:
                game.phase_duration_seconds = duration_seconds
                game.next_phase_at = datetime.utcnow() + timedelta(seconds=duration_seconds)
            else:
                game.phase_duration_seconds = None
                game.next_phase_at = None
            
            # Guardar usando el módulo database
            success = GameDatabaseService.save_game_extended(game)
            
            if success:
                logger.info(f"Fase actualizada para juego {game_id}: {new_phase.value}")
                if duration_seconds:
                    logger.info(f"Timer establecido: {duration_seconds}s")
            
            return success
                
        except Exception as e:
            logger.error(f"Error actualizando fase del juego {game_id}: {e}")
            return False
    
    @staticmethod
    def get_games_ready_for_phase_advance() -> List[GameExtended]:
        """
        Obtiene juegos listos para avanzar de fase automáticamente.
        
        Returns:
            Lista de juegos que deben avanzar de fase
        """
        try:
            # Obtener todos los juegos activos
            all_games = load_all_games()
            now = datetime.utcnow()
            ready_games = []
            
            for game in all_games:
                try:
                    # Convertir a GameExtended para verificar campos avanzados
                    game_extended = GameExtended.from_game(game)
                    
                    # Verificar si está listo para avanzar
                    if (game_extended.next_phase_at and 
                        game_extended.next_phase_at <= now and
                        game_extended.phase_auto_advance and
                        game_extended.status != GameStatus.FINISHED):
                        
                        ready_games.append(game_extended)
                        
                except Exception as e:
                    logger.error(f"Error verificando juego {game.id} para avance: {e}")
            
            if ready_games:
                logger.info(f"Encontrados {len(ready_games)} juegos listos para avanzar")
            
            return ready_games
                
        except Exception as e:
            logger.error(f"Error obteniendo juegos listos para avance: {e}")
            return []
    
    @staticmethod
    def record_player_action(game_id: str, user_id: str, 
                           action_type: str, action_data: Dict[str, Any]) -> bool:
        """
        Registra acción de jugador en base de datos.
        
        Args:
            game_id: ID del juego
            user_id: ID del usuario que realiza la acción
            action_type: Tipo de acción ("vote", "night_action", etc.)
            action_data: Datos específicos de la acción
            
        Returns:
            True si se registró correctamente
        """
        try:
            # Obtener juego actual
            game = GameDatabaseService.get_game_extended(game_id)
            if not game:
                logger.error(f"Juego {game_id} no encontrado para registrar acción")
                return False
            
            # Actualizar timestamp de actividad del jugador
            if not game.last_game_activity:
                game.last_game_activity = {}
            game.last_game_activity[user_id] = datetime.utcnow()
            
            # Registrar acción según el tipo
            if action_type == "vote":
                if not game.votes:
                    game.votes = {}
                game.votes[user_id] = action_data.get("target_id",'')
                if game.votes[user_id] == '':
                    del game.votes[user_id]
                    print(f"Usuario {user_id} ha retirado su voto en juego {game_id}")
                
            elif action_type == "night_action":
                if not game.pending_night_actions:
                    game.pending_night_actions = {}
                game.pending_night_actions[user_id] = action_data
                
            elif action_type == "sheriff_vote":
                if not game.votes:
                    game.votes = {}
                game.votes[user_id] = action_data.get("target_id", "")
            
            # Guardar cambios
            success = GameDatabaseService.save_game_extended(game)
            
            if success:
                logger.info(f"Acción registrada: {action_type} por {user_id} en juego {game_id}")
            
            return success
                
        except Exception as e:
            logger.error(f"Error registrando acción {action_type} en juego {game_id}: {e}")
            return False
    
    @staticmethod
    def advance_phase(game_id: str) -> Optional[GameExtended]:
        """
        Avanza la fase del juego según la lógica actual.
        
        Args:
            game_id: ID del juego
            
        Returns:
            GameExtended actualizado o None si hay error
        """
        try:
            game = GameDatabaseService.get_game_extended(game_id)
            if not game:
                return None
            
            # Determinar siguiente fase según la lógica actual
            next_phase = GameDatabaseService._get_next_phase(game.current_phase, game)
            
            if next_phase:
                # Obtener duración por defecto para la nueva fase
                duration = GameDatabaseService._get_phase_duration(next_phase)
                
                # Actualizar fase
                if GameDatabaseService.update_phase(game_id, next_phase, duration):
                    # Retornar juego actualizado
                    return GameDatabaseService.get_game_extended(game_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Error avanzando fase del juego {game_id}: {e}")
            return None
    
    @staticmethod
    def get_active_games() -> List[GameExtended]:
        """
        Obtiene todos los juegos activos (no terminados).
        
        Returns:
            Lista de juegos activos como GameExtended
        """
        try:
            all_games = load_all_games()
            active_games = []
            
            for game in all_games:
                if game.status in [GameStatus.WAITING, GameStatus.STARTING]:
                    try:
                        game_extended = GameExtended.from_game(game)
                        active_games.append(game_extended)
                    except Exception as e:
                        logger.error(f"Error convirtiendo juego activo {game.id}: {e}")
            
            return active_games
                
        except Exception as e:
            logger.error(f"Error obteniendo juegos activos: {e}")
            return []
    
    @staticmethod
    def save_game_extended(game: GameExtended) -> bool:
        """
        Guarda un GameExtended completo en base de datos.
        
        Args:
            game: GameExtended a guardar
            
        Returns:
            True si se guardó correctamente
        """
        try:
            # Usar directamente GameDB.from_game_extended para preservar todos los campos
            from app.database.session import SessionLocal
            from app.database.models import GameDB
            
            with SessionLocal() as session:
                # Verificar si el juego ya existe
                existing_game = session.query(GameDB).filter(GameDB.id == game.id).first()
                
                if existing_game:
                    # Actualizar juego existente usando from_game_extended
                    updated_game = GameDB.from_game_extended(game)
                    
                    # Copiar campos actualizados al objeto existente
                    for key, value in updated_game.__dict__.items():
                        if not key.startswith('_'):
                            setattr(existing_game, key, value)
                else:
                    # Crear nuevo juego
                    db_game = GameDB.from_game_extended(game)
                    session.add(db_game)
                
                session.commit()
                logger.info(f"GameExtended {game.id} guardado correctamente")
                return True
                
        except Exception as e:
            logger.error(f"Error guardando GameExtended {game.id}: {e}")
            return False
    
    # Métodos auxiliares privados
    
    @staticmethod
    def _get_next_phase(current_phase: GamePhase, game: GameExtended) -> Optional[GamePhase]:
        """
        Determina la siguiente fase según la lógica del juego.
        
        Args:
            current_phase: Fase actual
            game: Estado del juego
            
        Returns:
            Siguiente fase o None si no debe avanzar
        """
        # Mapeo básico de transiciones de fase
        phase_transitions = {
            GamePhase.WAITING: GamePhase.DAY_DISCUSSION,
            GamePhase.DAY_DISCUSSION: GamePhase.DAY_VOTING,
            GamePhase.DAY_VOTING: GamePhase.NIGHT_ACTIONS,
            GamePhase.NIGHT_ACTIONS: GamePhase.NIGHT_RESOLUTION,
            GamePhase.NIGHT_RESOLUTION: GamePhase.DAY_DISCUSSION,
        }
        
        # Verificar condiciones especiales
        if current_phase == GamePhase.NIGHT_RESOLUTION:
            # Verificar si el juego debe terminar
            if GameDatabaseService._should_game_end(game):
                return GamePhase.GAME_OVER
        
        return phase_transitions.get(current_phase)
    
    @staticmethod
    def _get_phase_duration(phase: GamePhase) -> Optional[int]:
        """
        Obtiene la duración por defecto de una fase.
        
        Args:
            phase: Fase del juego
            
        Returns:
            Duración en segundos o None para duración ilimitada
        """
        durations = {
            GamePhase.DAY_DISCUSSION: 300,  # 5 minutos
            GamePhase.DAY_VOTING: 120,      # 2 minutos
            GamePhase.NIGHT_ACTIONS: 180,   # 3 minutos
            GamePhase.NIGHT_RESOLUTION: 30, # 30 segundos
        }
        
        return durations.get(phase)
    
    @staticmethod
    def _should_game_end(game: GameExtended) -> bool:
        """
        Verifica si el juego debe terminar.
        
        Args:
            game: Estado del juego
            
        Returns:
            True si el juego debe terminar
        """
        # Lógica básica: implementar según reglas del juego
        # Por ahora, solo verificar si hay suficientes jugadores vivos
        if not game.players:
            return True
            
        alive_players = len([p for p in game.players.values() if p.is_alive])
        return alive_players < 3  # Mínimo 3 jugadores para continuar
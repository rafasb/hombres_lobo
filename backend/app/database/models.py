"""
Modelos SQLAlchemy para la base de datos
Contiene UserDB, GameDB con todas sus definiciones de columnas y métodos de conversión
"""

import json
from datetime import datetime, UTC
from typing import Dict
from sqlalchemy import Column, String, DateTime, Integer, Boolean
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON

from app.database.session import Base
from app.models.user import User, UserAccessRole, UserStatus
from app.models.game_and_player import Game, GameStatus, PlayerInfo, Roles
from app.models.game_extended import GameExtended, GamePhase


class UserDB(Base):
    """Modelo SQLAlchemy para la tabla users"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default=UserAccessRole.PLAYER.value)
    status = Column(String, nullable=False, default=UserStatus.DISCONNECTED.value)
    in_game = Column(Boolean, nullable=False, default=False)
    game_id = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    updated_at = Column(DateTime, nullable=False, default=datetime.now(), onupdate=datetime.utcnow)

    def to_pydantic(self) -> User:
        """Convierte el modelo SQLAlchemy a modelo Pydantic."""
        return User(
            id=getattr(self, 'id'),
            username=getattr(self, 'username'),
            email=getattr(self, 'email'),
            hashed_password=getattr(self, 'hashed_password'),
            role=UserAccessRole(getattr(self, 'role')),
            status=UserStatus(getattr(self, 'status')),
            game_id=getattr(self, 'game_id'),
            created_at=getattr(self, 'created_at').replace(tzinfo=UTC),
            updated_at=getattr(self, 'updated_at').replace(tzinfo=UTC)
        )

    @classmethod
    def from_pydantic(cls, user: User):
        """Crea un modelo SQLAlchemy desde un modelo Pydantic."""
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            role=user.role.value,
            status=user.status.value,
            game_id=user.game_id,
            created_at=user.created_at,
            updated_at=user.updated_at
        )


class GameDB(Base):
    """Modelo SQLAlchemy para la tabla games"""
    __tablename__ = "games"
    
    # Campos base del modelo Game original
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    creator_id = Column(String, nullable=False, index=True)
    max_players = Column(Integer, nullable=False, default=12)
    player_ids = Column(SQLiteJSON, nullable=False, default=list)
    players = Column(SQLiteJSON, nullable=False, default=dict)
    status = Column(String, nullable=False, default=GameStatus.WAITING.value)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    current_round = Column(Integer, nullable=False, default=0)
    is_first_night = Column(Boolean, nullable=False, default=True)
    night_actions = Column(SQLiteJSON, nullable=False, default=dict)
    # Campos actualizados para compatibilidad con Game
    defeated_players = Column(SQLiteJSON, nullable=False, default=list)
    connected_players = Column(SQLiteJSON, nullable=False, default=list)
    votes = Column(SQLiteJSON, nullable=False, default=dict)
    # Mantener day_votes por compatibilidad legacy
    day_votes = Column(SQLiteJSON, nullable=False, default=dict)
    
    # 🆕 FASE 2: Nuevos campos para migración de estado persistente
    # Gestión de Fases
    current_phase = Column(String, nullable=False, default="waiting")
    phase_start_time = Column(DateTime, nullable=True)
    phase_duration_seconds = Column(Integer, nullable=True)
    phase_auto_advance = Column(Boolean, nullable=False, default=True)
    
    # Temporizadores Persistentes (reemplazo de asyncio.create_task)
    next_phase_at = Column(DateTime, nullable=True)
    phase_end_actions = Column(SQLiteJSON, nullable=False, default=list)
    
    # Estado de Votación
    voting_active = Column(Boolean, nullable=False, default=False)
    voting_start_time = Column(DateTime, nullable=True)
    voting_end_time = Column(DateTime, nullable=True)
    voting_type = Column(String, nullable=True)  # "lynch", "sheriff", etc.
    
    # Acciones Nocturnas Ampliadas
    pending_night_actions = Column(SQLiteJSON, nullable=False, default=dict)
    completed_night_actions = Column(SQLiteJSON, nullable=False, default=list)
    night_action_deadline = Column(DateTime, nullable=True)
    
    # Metadata de Juego
    auto_advance_enabled = Column(Boolean, nullable=False, default=True)
    manual_control = Column(Boolean, nullable=False, default=False)
    game_speed = Column(String, nullable=False, default="normal")  # "slow", "normal", "fast"
    game_end_time = Column(DateTime, nullable=True)  # Timestamp cuando termina el juego
    
    # Estado de Actividad de Jugadores (Solo para gameplay, no conexiones WebSocket)
    last_game_activity = Column(SQLiteJSON, nullable=False, default=dict)
    inactive_players = Column(SQLiteJSON, nullable=False, default=list)

    def to_pydantic(self) -> Game:
        """Convierte el modelo SQLAlchemy a modelo Pydantic."""
        raw_players = getattr(self, 'players') or {}
        raw_player_ids = getattr(self, 'player_ids') or []

        players_dict: Dict[str, PlayerInfo] = {}

        # Procesar players dict (nuevo formato)
        if isinstance(raw_players, dict):
            for player_id, player_data in raw_players.items():
                try:
                    if isinstance(player_data, dict):
                        # Asegurar que player_id esté en los datos
                        player_data['player_id'] = player_id
                        # Validar y convertir role si es string
                        if 'role' in player_data and isinstance(player_data['role'], str):
                            try:
                                player_data['role'] = Roles(player_data['role'])
                            except ValueError:
                                player_data['role'] = Roles.VILLAGER
                        players_dict[player_id] = PlayerInfo(**player_data)
                    else:
                        # Fallback: crear PlayerInfo básico
                        players_dict[player_id] = PlayerInfo(
                            player_id=player_id,
                            role=Roles.VILLAGER
                        )
                except Exception as e:
                    print(f"Error procesando player {player_id}: {e}")
                    players_dict[player_id] = PlayerInfo(
                        player_id=player_id,
                        role=Roles.VILLAGER
                    )
        
        # Migración desde formato antiguo: si raw_players es lista
        elif isinstance(raw_players, list):
            # Intentar migrar desde el formato antiguo
            for item in raw_players:
                if isinstance(item, dict) and 'player_id' in item:
                    try:
                        # Validar role
                        if 'role' in item and isinstance(item['role'], str):
                            item['role'] = Roles(item['role'])
                        players_dict[item['player_id']] = PlayerInfo(**item)
                    except Exception as e:
                        print(f"Error migrando player {item.get('player_id', 'unknown')}: {e}")
                        players_dict[item['player_id']] = PlayerInfo(
                            player_id=item['player_id'],
                            role=Roles.VILLAGER
                        )
                elif isinstance(item, str):
                    # Formato muy antiguo: solo ID
                    players_dict[item] = PlayerInfo(
                        player_id=item,
                        role=Roles.VILLAGER
                    )

        return Game(
            name=getattr(self, 'name'),
            id=getattr(self, 'id'),
            creator_id=getattr(self, 'creator_id'),
            max_players=getattr(self, 'max_players'),
            player_ids=raw_player_ids,
            players=players_dict,
            status=GameStatus(getattr(self, 'status')),
            created_at=getattr(self, 'created_at').replace(tzinfo=UTC),
            current_round=getattr(self, 'current_round'),
            is_first_night=getattr(self, 'is_first_night'),
            night_actions=getattr(self, 'night_actions') or {},
            # Nuevos campos
            defeated_players=getattr(self, 'defeated_players') or [],
            connected_players=getattr(self, 'connected_players') or [],
            votes=getattr(self, 'votes') or getattr(self, 'day_votes') or {}  # Priorizar votes, fallback a day_votes
        )
    
    def to_game_extended(self) -> GameExtended:
        """Convierte el modelo SQLAlchemy a GameExtended con todos los nuevos campos."""
        # Primero obtener el Game base
        base_game = self.to_pydantic()
        
        # Convertir GameStatus a GamePhase (solo para fallback)
        status_to_phase = {
            "waiting": GamePhase.WAITING,
            "started": GamePhase.DAY_DISCUSSION,
            "night": GamePhase.NIGHT_ACTIONS,
            "day": GamePhase.DAY_DISCUSSION,
            "paused": GamePhase.PAUSED,
            "finished": GamePhase.GAME_OVER
        }
        
        # Obtener current_phase directamente o con fallback al status
        current_phase_str = getattr(self, 'current_phase', None)
        
        if current_phase_str:
            # El campo current_phase contiene valores de GamePhase directamente
            try:
                current_phase = GamePhase(current_phase_str)
            except ValueError:
                # Si el valor no es válido, usar WAITING como fallback
                current_phase = GamePhase.WAITING
        else:
            # Fallback al status del juego base usando mapeo
            current_phase = GamePhase(status_to_phase.get(base_game.status.value, GamePhase.WAITING))
        
        # Parsear campos JSON
        def safe_get_json(attr_name, default):
            try:
                value = getattr(self, attr_name, None)
                if value is None:
                    return default
                if isinstance(value, str):
                    return json.loads(value)
                return value
            except (json.JSONDecodeError, AttributeError):
                return default
        
        return GameExtended(
            # Campos base del Game original
            id=base_game.id,
            name=base_game.name,
            creator_id=base_game.creator_id,
            max_players=base_game.max_players,
            player_ids=base_game.player_ids,
            players=base_game.players,
            status=base_game.status,
            created_at=base_game.created_at,
            current_round=base_game.current_round,
            is_first_night=base_game.is_first_night,
            night_actions=base_game.night_actions,
            defeated_players=base_game.defeated_players,
            votes=base_game.votes,
            
            # 🆕 Nuevos campos extendidos
            # Gestión de Fases
            current_phase=current_phase,
            phase_start_time=getattr(self, 'phase_start_time', None),
            phase_duration_seconds=getattr(self, 'phase_duration_seconds', None),
            phase_auto_advance=getattr(self, 'phase_auto_advance', True),
            
            # Temporizadores Persistentes
            next_phase_at=getattr(self, 'next_phase_at', None),
            phase_end_actions=safe_get_json('phase_end_actions', []),
            
            # Estado de Votación
            voting_active=getattr(self, 'voting_active', False),
            voting_start_time=getattr(self, 'voting_start_time', None),
            voting_end_time=getattr(self, 'voting_end_time', None),
            voting_type=getattr(self, 'voting_type', None),
            
            # Acciones Nocturnas Ampliadas
            pending_night_actions=safe_get_json('pending_night_actions', {}),
            completed_night_actions=safe_get_json('completed_night_actions', []),
            night_action_deadline=getattr(self, 'night_action_deadline', None),
            
            # Metadata de Juego
            auto_advance_enabled=getattr(self, 'auto_advance_enabled', True),
            manual_control=getattr(self, 'manual_control', False),
            game_speed=getattr(self, 'game_speed', "normal"),
            game_end_time=getattr(self, 'game_end_time', None),
            
            # Estado de Actividad de Jugadores
            last_game_activity=safe_get_json('last_game_activity', {}),
            inactive_players=safe_get_json('inactive_players', [])
        )
    
    @classmethod
    def from_pydantic(cls, game: Game):
        """Crea un modelo SQLAlchemy desde un modelo Pydantic."""
        # Serializar players dict a una representación JSON-friendly
        serialized_players = {}
        
        for player_id, player_state in (game.players or {}).items():
            # Convertir PlayerInfo a dict
            if hasattr(player_state, 'model_dump'):
                player_dict = player_state.model_dump()
            elif hasattr(player_state, 'dict'):
                player_dict = player_state.dict()
            else:
                player_dict = dict(player_state) if isinstance(player_state, dict) else {}
            
            # Asegurar que player_id esté en el dict y que role sea string
            player_dict['player_id'] = player_id
            if 'role' in player_dict and hasattr(player_dict['role'], 'value'):
                player_dict['role'] = player_dict['role'].value
            
            serialized_players[player_id] = player_dict

        return cls(
            id=game.id,
            name=game.name,
            creator_id=game.creator_id,
            max_players=game.max_players,
            player_ids=game.player_ids or [],
            players=serialized_players,
            status=game.status.value,
            created_at=game.created_at,
            current_round=game.current_round,
            is_first_night=game.is_first_night,
            night_actions=game.night_actions or {},
            # Nuevos campos
            defeated_players=game.defeated_players or [],
            connected_players=game.connected_players or [],
            votes=game.votes or {},
            # Mantener day_votes por compatibilidad (usar votes como fuente principal)
            day_votes=game.votes or {}
        )
    
    @classmethod
    def from_game_extended(cls, game: GameExtended):
        """Crea un modelo SQLAlchemy desde un GameExtended."""
        # Serializar players dict (reutilizar lógica del from_pydantic)
        serialized_players = {}
        for player_id, player_state in (game.players or {}).items():
            if hasattr(player_state, 'model_dump'):
                player_dict = player_state.model_dump()
            elif hasattr(player_state, 'dict'):
                player_dict = player_state.dict()
            else:
                player_dict = dict(player_state) if isinstance(player_state, dict) else {}
            
            player_dict['player_id'] = player_id
            if 'role' in player_dict and hasattr(player_dict['role'], 'value'):
                player_dict['role'] = player_dict['role'].value
            
            serialized_players[player_id] = player_dict

        # Serializar campos datetime a timestamp ISO
        def serialize_datetime_dict(dt_dict):
            result = {}
            for key, value in dt_dict.items():
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                else:
                    result[key] = value
            return result

        return cls(
            # Campos base
            id=game.id,
            name=game.name,
            creator_id=game.creator_id,
            max_players=game.max_players,
            player_ids=game.player_ids or [],
            players=serialized_players,
            status=game.status.value,
            created_at=game.created_at,
            current_round=game.current_round,
            is_first_night=game.is_first_night,
            night_actions=game.night_actions or {},
            defeated_players=game.defeated_players or [],
            connected_players=game.connected_players or [],
            votes=game.votes or {},
            day_votes=game.votes or {},
            
            # 🆕 Nuevos campos extendidos
            # Gestión de Fases
            current_phase=game.current_phase.value,
            phase_start_time=game.phase_start_time,
            phase_duration_seconds=game.phase_duration_seconds,
            phase_auto_advance=game.phase_auto_advance,
            
            # Temporizadores Persistentes
            next_phase_at=game.next_phase_at,
            phase_end_actions=json.dumps(game.phase_end_actions),
            
            # Estado de Votación
            voting_active=game.voting_active,
            voting_start_time=game.voting_start_time,
            voting_end_time=game.voting_end_time,
            voting_type=game.voting_type,
            
            # Acciones Nocturnas Ampliadas
            pending_night_actions=json.dumps(game.pending_night_actions),
            completed_night_actions=json.dumps(game.completed_night_actions),
            night_action_deadline=game.night_action_deadline,
            
            # Metadata de Juego
            auto_advance_enabled=game.auto_advance_enabled,
            manual_control=game.manual_control,
            game_speed=game.game_speed,
            game_end_time=game.game_end_time,
            
            # Estado de Actividad de Jugadores
            last_game_activity=json.dumps(serialize_datetime_dict(game.last_game_activity)),
            inactive_players=json.dumps(game.inactive_players)
        )
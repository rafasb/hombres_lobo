import os
import json
import uuid
from typing import List, Optional, Generator, Dict
from datetime import datetime, UTC
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from app.models.user import User, UserAccessRole, UserStatus
from app.models.game_and_player import (
    Game,
    GameStatus,
    PlayerInfo,
    Roles,
)
from app.core.security import hash_password
from dotenv import load_dotenv

# Cargar variables de entorno
env_path = os.path.join(os.path.dirname(__file__), '../.env')
if not os.path.exists(env_path):
    env_example_path = os.path.join(os.path.dirname(__file__), '../.env.example')
    if os.path.exists(env_example_path):
        os.rename(env_example_path, env_path)
load_dotenv(env_path)

# Configuración de la base de datos
DB_DIR = os.path.join(os.path.dirname(__file__), 'db_sqlite')
os.makedirs(DB_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'hombres_lobo.db')}"

# Configuración SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos SQLAlchemy optimizados usando los modelos Pydantic
class UserDB(Base):
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
    def from_pydantic(cls, user: User) -> 'UserDB':
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
    __tablename__ = "games"
    
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
    eliminated_players = Column(SQLiteJSON, nullable=False, default=list)
    connected_players = Column(SQLiteJSON, nullable=False, default=list)
    votes = Column(SQLiteJSON, nullable=False, default=dict)
    # Mantener day_votes por compatibilidad legacy
    day_votes = Column(SQLiteJSON, nullable=False, default=dict)
    
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
            id=getattr(self, 'id'),
            name=getattr(self, 'name'),
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
            eliminated_players=getattr(self, 'eliminated_players') or [],
            connected_players=getattr(self, 'connected_players') or [],
            votes=getattr(self, 'votes') or getattr(self, 'day_votes') or {}  # Priorizar votes, fallback a day_votes
        )
    
    @classmethod
    def from_pydantic(cls, game: Game) -> 'GameDB':
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
            eliminated_players=game.eliminated_players or [],
            connected_players=game.connected_players or [],
            votes=game.votes or {},
            # Mantener day_votes por compatibilidad (usar votes como fuente principal)
            day_votes=game.votes or {}
        )

def check_and_migrate_database():
    """Verifica y migra la estructura de la base de datos si es necesario."""
    print("🔄 Verificando estructura de base de datos...")
    
    try:
        with engine.connect() as conn:
            # Verificar si existe la tabla games
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='games'
            """))
            
            if not result.fetchone():
                print("✅ Tabla games no existe, se creará nueva estructura")
                return True
            
            # Verificar columnas existentes en la tabla games
            result = conn.execute(text("PRAGMA table_info(games)"))
            columns = {row[1] for row in result.fetchall()}
            
            required_columns = {
                'id', 'name', 'creator_id', 'max_players', 'player_ids', 
                'players', 'status', 'created_at', 'current_round', 
                'is_first_night', 'night_actions', 'eliminated_players',
                'connected_players', 'votes', 'day_votes'
            }
            
            missing_columns = required_columns - columns
            
            if missing_columns:
                print(f"⚠️  Faltan columnas en tabla games: {missing_columns}")
                print("🔄 Migrando estructura de tabla games...")
                
                # Crear tabla temporal con nueva estructura
                conn.execute(text("""
                    CREATE TABLE games_new (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        creator_id TEXT NOT NULL,
                        max_players INTEGER NOT NULL DEFAULT 12,
                        player_ids TEXT NOT NULL DEFAULT '[]',
                        players TEXT NOT NULL DEFAULT '{}',
                        status TEXT NOT NULL DEFAULT 'waiting',
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        current_round INTEGER NOT NULL DEFAULT 0,
                        is_first_night BOOLEAN NOT NULL DEFAULT 1,
                        night_actions TEXT NOT NULL DEFAULT '{}',
                        eliminated_players TEXT NOT NULL DEFAULT '[]',
                        connected_players TEXT NOT NULL DEFAULT '[]',
                        votes TEXT NOT NULL DEFAULT '{}',
                        day_votes TEXT NOT NULL DEFAULT '{}'
                    )
                """))
                
                # Migrar datos existentes (solo columnas que coincidan)
                existing_columns = columns.intersection(required_columns)
                if existing_columns:
                    columns_str = ', '.join(existing_columns)
                    conn.execute(text(f"""
                        INSERT INTO games_new ({columns_str})
                        SELECT {columns_str} FROM games
                    """))
                
                # Reemplazar tabla antigua
                conn.execute(text("DROP TABLE games"))
                conn.execute(text("ALTER TABLE games_new RENAME TO games"))
                
                # Crear índices
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_games_creator_id ON games (creator_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_games_status ON games (status)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_games_created_at ON games (created_at)"))
                
                conn.commit()
                print("✅ Migración de tabla games completada")
            else:
                print("✅ Estructura de tabla games correcta")
                
    except Exception as e:
        print(f"❌ Error durante migración: {e}")
        raise
    
    return True

# Crear todas las tablas después de verificar migración
def initialize_database():
    """Inicializa la base de datos con verificación y migración."""
    print("🔄 Inicializando base de datos...")
    
    # Verificar y migrar si es necesario
    check_and_migrate_database()
    
    # Crear estructura completa
    Base.metadata.create_all(bind=engine)
    
    print("✅ Base de datos inicializada correctamente")

# Dependency para obtener la sesión de base de datos
@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager para obtener una sesión de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db() -> Generator[Session, None, None]:
    """Función para obtener una sesión de base de datos (para FastAPI dependency)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Funciones de migración desde JSON
def migrate_from_json():
    """Migra los datos existentes desde JSON a SQLite."""
    json_dir = os.path.join(os.path.dirname(__file__), 'db_json')
    
    if not os.path.exists(json_dir):
        print("📝 No se encontraron datos JSON para migrar.")
        return
    
    with get_db_session() as db:
        # Migrar usuarios
        users_file = os.path.join(json_dir, 'users.json')
        if os.path.exists(users_file):
            with open(users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            migrated_users = 0
            for user_data in users_data.values():
                # Verificar si el usuario ya existe
                existing_user = db.query(UserDB).filter(UserDB.id == user_data['id']).first()
                if not existing_user:
                    # Convertir fechas string a datetime
                    created_at = datetime.fromisoformat(user_data['created_at']) if isinstance(user_data['created_at'], str) else user_data['created_at']
                    updated_at = datetime.fromisoformat(user_data['updated_at']) if isinstance(user_data['updated_at'], str) else user_data['updated_at']
                    
                    db_user = UserDB(
                        id=user_data['id'],
                        username=user_data['username'],
                        email=user_data['email'],
                        hashed_password=user_data['hashed_password'],
                        role=user_data['role'],
                        status=user_data['status'],
                        created_at=created_at,
                        updated_at=updated_at
                    )
                    db.add(db_user)
                    migrated_users += 1
            
            if migrated_users > 0:
                print(f"📦 Migrados {migrated_users} usuarios desde JSON")
        
        # Migrar partidas
        games_file = os.path.join(json_dir, 'games.json')
        if os.path.exists(games_file):
            with open(games_file, 'r', encoding='utf-8') as f:
                games_data = json.load(f)
            
            migrated_games = 0
            for game_data in games_data.values():
                # Verificar si la partida ya existe
                existing_game = db.query(GameDB).filter(GameDB.id == game_data['id']).first()
                if not existing_game:
                    # Convertir fecha string a datetime
                    created_at = datetime.fromisoformat(game_data['created_at']) if isinstance(game_data['created_at'], str) else game_data['created_at']
                    
                    # Migrar formato antiguo de players y roles al nuevo formato
                    players_dict = {}
                    old_players = game_data.get('players', [])
                    old_roles = game_data.get('roles', {})
                    
                    # Si players es una lista (formato antiguo)
                    if isinstance(old_players, list):
                        for player_item in old_players:
                            if isinstance(player_item, str):
                                # Solo ID de jugador
                                player_id = player_item
                                role_info = old_roles.get(player_id, {})
                                players_dict[player_id] = {
                                    'player_id': player_id,
                                    'role': role_info.get('role', 'villager'),
                                    'is_alive': role_info.get('is_alive', True)
                                }
                            elif isinstance(player_item, dict) and 'player_id' in player_item:
                                # Ya tiene formato dict
                                players_dict[player_item['player_id']] = player_item
                    
                    # Si players ya es dict (formato nuevo)
                    elif isinstance(old_players, dict):
                        players_dict = old_players
                    
                    db_game = GameDB(
                        id=game_data['id'],
                        name=game_data['name'],
                        creator_id=game_data['creator_id'],
                        player_ids=game_data.get('player_ids', []),
                        players=players_dict,
                        status=game_data['status'],
                        created_at=created_at,
                        current_round=game_data.get('current_round', 0),
                        is_first_night=game_data.get('is_first_night', True),
                        night_actions=game_data.get('night_actions', {}),
                        # Nuevos campos con fallbacks apropiados
                        eliminated_players=game_data.get('eliminated_players', []),
                        connected_players=game_data.get('connected_players', []),
                        votes=game_data.get('votes', game_data.get('day_votes', {})),  # Priorizar votes
                        day_votes=game_data.get('day_votes', {}),  # Mantener por compatibilidad
                        max_players=game_data.get('max_players', 12)
                    )
                    db.add(db_game)
                    migrated_games += 1
            
            if migrated_games > 0:
                print(f"📦 Migradas {migrated_games} partidas desde JSON")
        
        db.commit()

# Ejecutar inicialización al cargar el módulo
try:
    initialize_database()
    
    # Intentar migración desde JSON si la base de datos está vacía
    with get_db_session() as db:
        user_count = db.query(UserDB).count()
        if user_count == 0:
            print("📦 Base de datos vacía, ejecutando migración desde JSON...")
            migrate_from_json()
except Exception as e:
    print(f"⚠️  Error durante la inicialización automática: {e}")

# Crear usuario admin por defecto
admin_username = os.getenv('ADMIN_USERNAME')
admin_email = os.getenv('ADMIN_EMAIL')
admin_password = os.getenv('ADMIN_PASSWORD')

if admin_username and admin_email and admin_password:
    try:
        with get_db_session() as db:
            existing_admin = db.query(UserDB).filter(UserDB.username == admin_username).first()
            if not existing_admin:
                admin_user = UserDB(
                    id=str(uuid.uuid4()),
                    username=admin_username,
                    email=admin_email,
                    hashed_password=hash_password(admin_password),
                    role=UserAccessRole.ADMIN.value,
                    status=UserStatus.DISCONNECTED.value,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC)
                )
                db.add(admin_user)
                db.commit()
                print(f"👑 Usuario admin creado: {admin_username}")
    except Exception as e:
        print(f"❌ Error creando usuario admin: {e}")

# --- Funciones específicas para usuarios optimizadas ---

def save_user(user: User) -> None:
    """Guarda un usuario en la base de datos."""
    with get_db_session() as db:
        db_user = db.query(UserDB).filter(UserDB.id == user.id).first()
        if db_user:
            # Actualizar usando el modelo Pydantic
            new_db_user = UserDB.from_pydantic(user)
            for attr, value in new_db_user.__dict__.items():
                if not attr.startswith('_'):
                    setattr(db_user, attr, value)
        else:
            # Crear nuevo usuario usando el modelo Pydantic
            db_user = UserDB.from_pydantic(user)
            db.add(db_user)
        
        db.commit()

def load_user(user_id: str) -> Optional[User]:
    """Carga un usuario por id."""
    with get_db_session() as db:
        db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
        return db_user.to_pydantic() if db_user else None

def load_all_users() -> List[User]:
    """Carga todos los usuarios."""
    with get_db_session() as db:
        return [db_user.to_pydantic() for db_user in db.query(UserDB).all()]

def delete_user(user_id: str) -> bool:
    """Elimina un usuario de la base de datos."""
    with get_db_session() as db:
        db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
        if db_user:
            db.delete(db_user)
            db.commit()
            return True
        return False

def find_user_by_username(username: str) -> Optional[User]:
    """Busca un usuario por nombre de usuario."""
    with get_db_session() as db:
        db_user = db.query(UserDB).filter(UserDB.username == username).first()
        return db_user.to_pydantic() if db_user else None

def find_user_by_email(email: str) -> Optional[User]:
    """Busca un usuario por email."""
    with get_db_session() as db:
        db_user = db.query(UserDB).filter(UserDB.email == email).first()
        return db_user.to_pydantic() if db_user else None

# --- Funciones específicas para partidas optimizadas ---

def save_game(game: Game) -> None:
    """Guarda una partida en la base de datos."""
    with get_db_session() as db:
        db_game = db.query(GameDB).filter(GameDB.id == game.id).first()
        if db_game:
            # Actualizar usando el modelo Pydantic
            new_db_game = GameDB.from_pydantic(game)
            for attr, value in new_db_game.__dict__.items():
                if not attr.startswith('_'):
                    setattr(db_game, attr, value)
        else:
            # Crear nueva partida usando el modelo Pydantic
            db_game = GameDB.from_pydantic(game)
            db.add(db_game)
        
        db.commit()

def load_game(game_id: str) -> Optional[Game]:
    """Carga una partida por id."""
    with get_db_session() as db:
        db_game = db.query(GameDB).filter(GameDB.id == game_id).first()
        return db_game.to_pydantic() if db_game else None

def load_all_games() -> List[Game]:
    """Carga todas las partidas."""
    with get_db_session() as db:
        return [db_game.to_pydantic() for db_game in db.query(GameDB).all()]

def delete_game(game_id: str) -> bool:
    """Elimina una partida de la base de datos."""
    with get_db_session() as db:
        db_game = db.query(GameDB).filter(GameDB.id == game_id).first()
        if db_game:
            db.delete(db_game)
            db.commit()
            return True
        return False

def find_games_by_creator(creator_id: str) -> List[Game]:
    """Encuentra todas las partidas creadas por un usuario."""
    with get_db_session() as db:
        return [db_game.to_pydantic() for db_game in db.query(GameDB).filter(GameDB.creator_id == creator_id).all()]

def find_games_by_status(status: str) -> List[Game]:
    """Encuentra todas las partidas con un estado específico."""
    with get_db_session() as db:
        return [db_game.to_pydantic() for db_game in db.query(GameDB).filter(GameDB.status == status).all()]

# --- Funciones helper optimizadas ---

def get_game_players(game: Game) -> List[User]:
    """Obtiene la lista completa de usuarios de una partida a partir de sus IDs."""
    # Obtener IDs de players dict (jugadores con roles asignados)
    player_ids = list(game.players.keys()) if game.players else []
    
    # Si no hay players con roles, usar player_ids (jugadores unidos pero sin roles)
    if not player_ids and game.player_ids:
        player_ids = game.player_ids

    with get_db_session() as db:
        if not player_ids:
            return []
        db_users = db.query(UserDB).filter(UserDB.id.in_(player_ids)).all()
        return [db_user.to_pydantic() for db_user in db_users]

# --- Funciones helper para gestión optimizada de jugadores en partidas ---

def get_game_player_by_id(game: Game, player_id: str) -> Optional[User]:
    """Obtiene un jugador específico de una partida por su ID."""
    # Buscar en players dict primero
    if game.players and player_id in game.players:
        return load_user(player_id)
    
    # Buscar en player_ids como fallback
    if game.player_ids and player_id in game.player_ids:
        return load_user(player_id)
    
    return None

def get_game_with_players(game_id: str) -> Optional[tuple[Game, List[User]]]:
    """Carga una partida junto con la información completa de sus jugadores."""
    game = load_game(game_id)
    if game:
        players = get_game_players(game)
        return game, players
    return None

def game_to_response(game: Game) -> dict:
    """Convierte un objeto Game a un diccionario de respuesta con información completa de jugadores."""
    
    # Obtener información completa de los jugadores
    players_info = []
    
    # Primero procesar players con roles asignados
    for player_id, player_state in (game.players or {}).items():
        user = load_user(player_id)
        if user:
            # Incluir información del rol del juego
            players_info.append({
                "id": user.id,
                "username": user.username,
                "role": user.role.value,
                "status": user.status.value,
                "game_role": player_state.role.value,
                "is_alive": player_state.is_alive,
                "has_acted_tonight": player_state.has_acted_tonight,
                "lover_partner_id": player_state.lover_partner_id
            })
    
    # Luego procesar player_ids que no tengan rol asignado aún
    for player_id in (game.player_ids or []):
        if player_id not in (game.players or {}):
            user = load_user(player_id)
            if user:
                players_info.append({
                    "id": user.id,
                    "username": user.username,
                    "role": user.role.value,
                    "status": user.status.value,
                    "game_role": None,
                    "is_alive": True,
                    "has_acted_tonight": False,
                    "lover_partner_id": None
                })
    
    # Crear el diccionario de respuesta
    response_data = game.model_dump()
    response_data["players"] = players_info
    
    return response_data
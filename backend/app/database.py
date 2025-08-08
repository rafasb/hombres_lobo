import os
import json
import uuid
from typing import Any, List, Optional, Generator
from datetime import datetime, UTC
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from app.models.user import User, UserRole, UserStatus
from app.models.game_and_roles import Game, GameStatus, GameResponse
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
    role = Column(String, nullable=False, default=UserRole.PLAYER.value)
    status = Column(String, nullable=False, default=UserStatus.ACTIVE.value)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    updated_at = Column(DateTime, nullable=False, default=datetime.now(), onupdate=datetime.utcnow)
    
    def to_pydantic(self) -> User:
        """Convierte el modelo SQLAlchemy a modelo Pydantic."""
        return User(
            id=self.id,
            username=self.username,
            email=self.email,
            hashed_password=self.hashed_password,
            role=UserRole(self.role),
            status=UserStatus(self.status),
            created_at=self.created_at.replace(tzinfo=UTC),
            updated_at=self.updated_at.replace(tzinfo=UTC)
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
            created_at=user.created_at,
            updated_at=user.updated_at
        )

class GameDB(Base):
    __tablename__ = "games"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    creator_id = Column(String, nullable=False, index=True)
    players = Column(SQLiteJSON, nullable=False, default=list)
    roles = Column(SQLiteJSON, nullable=False, default=dict)
    status = Column(String, nullable=False, default=GameStatus.WAITING.value)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    current_round = Column(Integer, nullable=False, default=0)
    is_first_night = Column(Boolean, nullable=False, default=True)
    night_actions = Column(SQLiteJSON, nullable=False, default=dict)
    day_votes = Column(SQLiteJSON, nullable=False, default=dict)
    max_players = Column(Integer, nullable=False, default=12)
    
    def to_pydantic(self) -> Game:
        """Convierte el modelo SQLAlchemy a modelo Pydantic."""
        return Game(
            id=self.id,
            name=self.name,
            creator_id=self.creator_id,
            players=self.players,
            roles=self.roles,
            status=GameStatus(self.status),
            created_at=self.created_at.replace(tzinfo=UTC),
            current_round=self.current_round,
            is_first_night=self.is_first_night,
            night_actions=self.night_actions,
            day_votes=self.day_votes,
            max_players=self.max_players
        )
    
    @classmethod
    def from_pydantic(cls, game: Game) -> 'GameDB':
        """Crea un modelo SQLAlchemy desde un modelo Pydantic."""
        return cls(
            id=game.id,
            name=game.name,
            creator_id=game.creator_id,
            players=game.players,
            roles=game.roles,
            status=game.status.value,
            created_at=game.created_at,
            current_round=game.current_round,
            is_first_night=game.is_first_night,
            night_actions=game.night_actions,
            day_votes=game.day_votes,
            max_players=game.max_players
        )

# Crear todas las tablas
Base.metadata.create_all(bind=engine)

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
        print("No se encontraron datos JSON para migrar.")
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
            
            print(f"Migrados {migrated_users} usuarios desde JSON")
        
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
                    
                    db_game = GameDB(
                        id=game_data['id'],
                        name=game_data['name'],
                        creator_id=game_data['creator_id'],
                        players=game_data['players'],
                        roles=game_data['roles'],
                        status=game_data['status'],
                        created_at=created_at,
                        current_round=game_data['current_round'],
                        is_first_night=game_data['is_first_night'],
                        night_actions=game_data['night_actions'],
                        day_votes=game_data['day_votes'],
                        max_players=game_data['max_players']
                    )
                    db.add(db_game)
                    migrated_games += 1
            
            print(f"Migradas {migrated_games} partidas desde JSON")
        
        db.commit()

# Ejecutar migración al inicializar si es necesario
try:
    with get_db_session() as db:
        user_count = db.query(UserDB).count()
        if user_count == 0:
            print("Base de datos vacía, ejecutando migración desde JSON...")
            migrate_from_json()
except Exception as e:
    print(f"Error durante la migración: {e}")

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
                    role=UserRole.ADMIN.value,
                    status=UserStatus.ACTIVE.value,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC)
                )
                db.add(admin_user)
                db.commit()
                print(f"Usuario admin creado: {admin_username}")
    except Exception as e:
        print(f"Error creando usuario admin: {e}")

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
    with get_db_session() as db:
        db_users = db.query(UserDB).filter(UserDB.id.in_(game.players)).all()
        return [db_user.to_pydantic() for db_user in db_users]

def game_to_game_response(game: Game) -> GameResponse:
    """Convierte un objeto Game a un objeto GameResponse con información completa de jugadores."""
    # Obtener información completa de los jugadores de forma optimizada
    players_info = []
    with get_db_session() as db:
        db_users = db.query(UserDB).filter(UserDB.id.in_(game.players)).all()
        for db_user in db_users:
            players_info.append({
                "id": db_user.id,
                "username": db_user.username,
                "role": db_user.role,
                "status": db_user.status
            })
    
    return GameResponse(
        id=game.id,
        name=game.name,
        creator_id=game.creator_id,
        players=players_info,
        roles=game.roles,
        status=game.status,
        created_at=game.created_at,
        current_round=game.current_round,
        is_first_night=game.is_first_night,
        night_actions=game.night_actions,
        day_votes=game.day_votes,
        max_players=game.max_players
    )

# --- Funciones helper para gestión optimizada de jugadores en partidas ---

def get_game_player_by_id(game: Game, player_id: str) -> Optional[User]:
    """Obtiene un jugador específico de una partida por su ID."""
    if player_id in game.players:
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
    for player_id in game.players:
        user = load_user(player_id)
        if user:
            # Solo incluimos información no sensible para la API
            players_info.append({
                "id": user.id,
                "username": user.username,
                "role": user.role.value,
                "status": user.status.value
            })
    
    # Crear el diccionario de respuesta
    response_data = game.model_dump()
    response_data["players"] = players_info
    
    return response_data

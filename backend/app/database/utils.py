"""
Funciones de utilidades y operaciones CRUD para la base de datos
Contiene todas las funciones save, load, delete, find y helpers
"""

import os
import json
import uuid
from typing import List, Optional, Tuple
from datetime import datetime, UTC
from contextlib import contextmanager

from app.database.session import SessionLocal
from app.database.models import UserDB, GameDB
from app.models.user import User, UserAccessRole, UserStatus
from app.models.game_and_player import Game
from app.core.security import hash_password


@contextmanager
def get_db_session():
    """Context manager para obtener una sesión de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Funciones de migración ---

def migrate_from_json():
    """Migra los datos existentes desde JSON a SQLite."""
    json_dir = os.path.join(os.path.dirname(__file__), '../db_json')
    
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
                        defeated_players=game_data.get('defeated_players', []),
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


def create_admin_user():
    """Crear usuario admin por defecto si está configurado en .env"""
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


# --- Funciones específicas para usuarios ---

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


# --- Funciones específicas para partidas ---

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


def find_games_by_player_id(player_id: str) -> List[Game]:
    """Encuentra todas las partidas en las que participa un jugador específico."""
    with get_db_session() as db:
        return [db_game.to_pydantic() for db_game in db.query(GameDB).filter(GameDB.player_ids.contains([player_id])).all()]


# --- Funciones helper ---

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


def get_game_player_by_id(game: Game, player_id: str) -> Optional[User]:
    """Obtiene un jugador específico de una partida por su ID."""
    # Buscar en players dict primero
    if game.players and player_id in game.players:
        return load_user(player_id)
    
    # Buscar en player_ids como fallback
    if game.player_ids and player_id in game.player_ids:
        return load_user(player_id)
    
    return None


def get_game_with_players(game_id: str) -> Optional[Tuple[Game, List[User]]]:
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
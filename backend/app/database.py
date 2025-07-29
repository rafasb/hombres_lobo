import os
import json
import uuid
from typing import Any, List, Optional
from app.models.user import User
from app.models.game_and_roles import Game
from datetime import datetime, UTC
from app.core.security import hash_password
from app.models.user import UserRole
from dotenv import load_dotenv

# Cargar variables de entorno
# se cargarán de .env y si no existe de .env.example
if not os.path.exists(os.path.join(os.path.dirname(__file__), '../.env')):
    os.rename(os.path.join(os.path.dirname(__file__), '../.env.example'), os.path.join(os.path.dirname(__file__), '../.env'))
else:
    load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

# Directorio donde se almacenarán los ficheros JSON
DB_DIR = os.path.join(os.path.dirname(__file__), 'db_json')
os.makedirs(DB_DIR, exist_ok=True)

# Inicializar ficheros si no existen
def ensure_json_file(filename: str, empty_obj: Any = {}):
    path = os.path.join(DB_DIR, filename)
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(empty_obj, f)

ensure_json_file('users.json', {})
ensure_json_file('games.json', {})

# Crear usuario admin por defecto si no existe
admin_username = os.getenv('ADMIN_USERNAME')
admin_email = os.getenv('ADMIN_EMAIL')
admin_password = os.getenv('ADMIN_PASSWORD')

# Crear admin directamente usando funciones locales
users = None
try:
    with open(os.path.join(DB_DIR, 'users.json'), 'r', encoding='utf-8') as f:
        users = json.load(f)
except Exception:
    users = {}

if admin_username and admin_email and admin_password:
    if not any(u.get('username') == admin_username for u in users.values()):
        admin = User(
            id=str(uuid.uuid4()),
            username=admin_username,
            email=admin_email,
            hashed_password=hash_password(admin_password),
            role=UserRole.ADMIN,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        users[admin.id] = admin.model_dump()
        # Serializar datetime
        for field in ["created_at", "updated_at"]:
            if isinstance(users[admin.id][field], datetime):
                users[admin.id][field] = users[admin.id][field].isoformat()
        with open(os.path.join(DB_DIR, 'users.json'), 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

def get_json_path(filename: str) -> str:
    """Devuelve la ruta absoluta de un fichero JSON en la base de datos."""
    return os.path.join(DB_DIR, f"{filename}.json")

def save_json(filename: str, data: Any) -> None:
    """Guarda datos en un fichero JSON."""
    with open(get_json_path(filename), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(filename: str) -> Any:
    """Carga datos de un fichero JSON. Devuelve None si no existe."""
    path = get_json_path(filename)
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- Funciones específicas para usuarios ---

def save_user(user: User) -> None:
    """Guarda un usuario en la base de datos (por id), serializando datetime."""
    users = load_json('users') or {}
    user_dict = user.model_dump()
    # Serializar datetime a string ISO
    for field in ["created_at", "updated_at"]:
        if isinstance(user_dict.get(field), datetime):
            user_dict[field] = user_dict[field].isoformat()
    users[user.id] = user_dict
    save_json('users', users)

def load_user(user_id: str) -> Optional[User]:
    """Carga un usuario por id, deserializando datetime."""
    users = load_json('users')
    if users and user_id in users:
        data = users[user_id]
        for field in ["created_at", "updated_at"]:
            if field in data and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field])
        return User(**data)
    return None

def load_all_users() -> List[User]:
    """Carga todos los usuarios, deserializando datetime."""
    users = load_json('users')
    if not users:
        return []
    result = []
    for u in users.values():
        for field in ["created_at", "updated_at"]:
            if field in u and isinstance(u[field], str):
                u[field] = datetime.fromisoformat(u[field])
        result.append(User(**u))
    return result

def delete_user(user_id: str) -> bool:
    """Elimina un usuario de la base de datos por su id. Devuelve True si existía y fue eliminado."""
    users = load_json('users') or {}
    if user_id in users:
        del users[user_id]
        save_json('users', users)
        return True
    return False

# --- Funciones específicas para partidas ---

def save_game(game: Game) -> None:
    """Guarda una partida en la base de datos (por id), serializando datetime."""
    games = load_json('games') or {}
    game_dict = game.model_dump()
    # Serializar datetime a string ISO
    if isinstance(game_dict.get('created_at'), datetime):
        game_dict['created_at'] = game_dict['created_at'].isoformat()
    
    # Serializar datetime en los objetos User de la lista de jugadores
    if 'players' in game_dict and game_dict['players']:
        for player in game_dict['players']:
            if isinstance(player.get('created_at'), datetime):
                player['created_at'] = player['created_at'].isoformat()
            if isinstance(player.get('updated_at'), datetime):
                player['updated_at'] = player['updated_at'].isoformat()
    
    games[game.id] = game_dict
    save_json('games', games)

def load_game(game_id: str) -> Optional[Game]:
    """Carga una partida por id, deserializando datetime."""
    games = load_json('games')
    if games and game_id in games:
        data = games[game_id]
        # Deserializar string ISO a datetime
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        # Deserializar datetime en los objetos User de la lista de jugadores
        if 'players' in data and data['players']:
            for player in data['players']:
                if 'created_at' in player and isinstance(player['created_at'], str):
                    player['created_at'] = datetime.fromisoformat(player['created_at'])
                if 'updated_at' in player and isinstance(player['updated_at'], str):
                    player['updated_at'] = datetime.fromisoformat(player['updated_at'])
        
        return Game(**data)
    return None

def load_all_games() -> List[Game]:
    """Carga todas las partidas, deserializando datetime."""
    games = load_json('games')
    if not games:
        return []
    result = []
    for g in games.values():
        if 'created_at' in g and isinstance(g['created_at'], str):
            g['created_at'] = datetime.fromisoformat(g['created_at'])
        result.append(Game(**g))
    return result

def delete_game(game_id: str) -> bool:
    """Elimina una partida de la base de datos por su id. Devuelve True si existía y fue eliminada."""
    games = load_json('games') or {}
    if game_id in games:
        del games[game_id]
        save_json('games', games)
        return True
    return False

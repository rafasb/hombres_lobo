import os
import json
from typing import Any, List, Optional
from app.models.user import User
from app.models.game import Game
from datetime import datetime

# Configuración y conexión a la base de datos

# Directorio donde se almacenarán los ficheros JSON
DB_DIR = os.path.join(os.path.dirname(__file__), 'db_json')

# Crear el directorio si no existe
os.makedirs(DB_DIR, exist_ok=True)

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
    """Guarda un usuario en la base de datos (por id)."""
    users = load_json('users') or {}
    users[user.id] = user.dict()
    save_json('users', users)

def load_user(user_id: str) -> Optional[User]:
    """Carga un usuario por id."""
    users = load_json('users')
    if users and user_id in users:
        return User(**users[user_id])
    return None

def load_all_users() -> List[User]:
    """Carga todos los usuarios."""
    users = load_json('users')
    if not users:
        return []
    return [User(**u) for u in users.values()]

# --- Funciones específicas para partidas ---

def save_game(game: Game) -> None:
    """Guarda una partida en la base de datos (por id), serializando datetime."""
    games = load_json('games') or {}
    game_dict = game.dict()
    # Serializar datetime a string ISO
    if isinstance(game_dict.get('created_at'), datetime):
        game_dict['created_at'] = game_dict['created_at'].isoformat()
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

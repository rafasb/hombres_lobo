"""
Módulo de servicios para la gestión de partidas.
Incluye funciones para crear, obtener y listar partidas usando la base de datos JSON.
"""

from app.database import save_game, load_game, load_all_games
from app.models.game import Game, GameStatus
from typing import Optional, List

# Lógica relacionada con partidas

def create_game(game: Game) -> None:
    save_game(game)

def get_game(game_id: str) -> Optional[Game]:
    return load_game(game_id)

def get_all_games() -> List[Game]:
    return load_all_games()

def delete_game(game_id: str) -> bool:
    """Elimina una partida de la base de datos por su id. Devuelve True si existía y fue eliminada."""
    from app.database import load_json, save_json
    games = load_json('games') or {}
    if game_id in games:
        del games[game_id]
        save_json('games', games)
        return True
    return False

def leave_game(game_id: str, user_id: str) -> bool:
    """Permite que un usuario abandone una partida si es jugador y la partida no ha comenzado."""
    from app.database import load_game, save_game
    game = load_game(game_id)
    if not game:
        return False
    # Solo puede abandonar si la partida está en estado WAITING
    if hasattr(game, 'status') and getattr(game, 'status', None) != 'waiting':
        return False
    # Eliminar al usuario de la lista de jugadores
    if hasattr(game, 'players'):
        original_count = len(game.players)
        game.players = [p for p in game.players if getattr(p, 'id', None) != user_id]
        if len(game.players) == original_count:
            return False  # No estaba en la partida
        save_game(game)
        return True
    return False

def update_game_params(game_id: str, user_id: str, name: str | None = None, max_players: int | None = None, roles: dict | None = None, is_admin: bool = False) -> Optional[Game]:
    """Permite al creador o admin modificar nombre, max_players y roles antes de que comience la partida."""
    game = load_game(game_id)
    if not game:
        return None
    # Solo el creador o admin pueden modificar, y solo si está en estado WAITING
    if not is_admin and (game.creator_id != user_id or game.status != GameStatus.WAITING):
        return None
    # Admin puede modificar en cualquier momento, creador solo en WAITING
    if not is_admin and game.status != GameStatus.WAITING:
        return None
    if name is not None:
        game.name = name
    if max_players is not None:
        game.max_players = max_players
    if roles is not None:
        game.roles = roles
    save_game(game)
    return game

def change_game_status(game_id: str, user_id: str, new_status: GameStatus, is_admin: bool = False) -> Optional[Game]:
    """Permite al creador o admin iniciar, pausar, avanzar fase o detener la partida."""
    game = load_game(game_id)
    if not game:
        return None
    # Solo el creador o admin pueden cambiar el estado
    if not is_admin and game.creator_id != user_id:
        return None
    # Lógica de transición de estados
    allowed = False
    if new_status == GameStatus.STARTED and game.status == GameStatus.WAITING:
        allowed = True
    elif new_status == GameStatus.NIGHT and game.status in [GameStatus.STARTED, GameStatus.DAY]:
        allowed = True
    elif new_status == GameStatus.DAY and game.status == GameStatus.NIGHT:
        allowed = True
    elif new_status == GameStatus.FINISHED and game.status in [GameStatus.STARTED, GameStatus.NIGHT, GameStatus.DAY]:
        allowed = True
    elif new_status == GameStatus.WAITING and game.status == GameStatus.PAUSED:
        allowed = True
    elif new_status == GameStatus.PAUSED and game.status in [GameStatus.STARTED, GameStatus.NIGHT, GameStatus.DAY]:
        allowed = True
    if not allowed:
        return None
    game.status = new_status
    save_game(game)
    return game

def creator_delete_game(game_id: str, user_id: str, is_admin: bool = False) -> bool:
    """Permite al creador o admin eliminar la partida si está en estado WAITING o PAUSED."""
    game = load_game(game_id)
    if not game:
        return False
    # Admin puede eliminar cualquier partida, creador solo las suyas en WAITING o PAUSED
    if not is_admin and (game.creator_id != user_id or game.status not in [GameStatus.WAITING, GameStatus.PAUSED]):
        return False
    return delete_game(game_id)

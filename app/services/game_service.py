"""
Módulo de servicios para la gestión de partidas.
Incluye funciones para crear, obtener y listar partidas usando la base de datos JSON.
"""

from app.database import save_game, load_game, load_all_games
from app.models.game import Game
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

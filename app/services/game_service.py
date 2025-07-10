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

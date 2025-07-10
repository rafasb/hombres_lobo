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

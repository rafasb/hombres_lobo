"""
Módulo de servicios para la gestión de partidas.
Incluye funciones para crear, obtener y listar partidas usando la base de datos SQLite.
"""

from app.database import save_game, load_game, load_all_games, delete_game as db_delete_game
from app.models.game_and_player import Game, GameStatus, PlayerInfo, Roles
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
    return db_delete_game(game_id)

def leave_game(game_id: str, user_id: str) -> bool:
    """Permite que un usuario abandone una partida.
    
    - Si la partida está en WAITING: se elimina su id de `player_ids`.
    - Si la partida ya ha comenzado (u otra fase): se elimina su entrada de `players` (dict).
    """
    game = load_game(game_id)
    if not isinstance(game, Game):
        return False

    modified = False

    # Si la partida está en WAITING, eliminamos de la lista de ids (antes de empezar)
    if game.status == GameStatus.WAITING:
        if user_id in game.player_ids:
            game.player_ids.remove(user_id)
            modified = True
            print(f"Usuario {user_id} eliminado de player_ids en partida {game_id}")
            game.remove_connected_player(user_id)
            print(f"Usuario {user_id} eliminado de connected_players en partida {game_id}")

    # Si la partida ya ha comenzado (o en cualquier otro estado), eliminar del dict de players si existe
    if user_id in game.players:
        # eliminar del dict de PlayerState
        game.players.pop(user_id, None)
        # también intentamos limpiar de player_ids por consistencia
        if user_id in game.player_ids:
            try:
                game.player_ids.remove(user_id)
            except ValueError:
                print(f"Warning: user_id {user_id} not found in player_ids during leave_game cleanup.")
        modified = True

    if modified:
        save_game(game)
        return True

    return False

def update_game_params(game_id: str, user_id: str, name: str | None = None, max_players: int | None = None, is_admin: bool = False) -> Optional[Game]:
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

def join_game(game_id: str, user_id: str) -> bool:
    """Permite que un usuario se una a una partida si está en estado WAITING y hay espacios disponibles."""
    game = load_game(game_id)
    if not game:
        return False
    
    # Solo se puede unir si la partida está en estado WAITING
    if game.status != GameStatus.WAITING:
        return False
    
    # Verificar que no haya alcanzado el máximo de jugadores
    if len(game.players) >= game.max_players:
        return False
    
    # Verificar que el usuario no esté ya en la partida (ahora comparamos IDs)
    if user_id in game.players:
        return False
    
    # Agregar el ID del usuario a la lista de jugadores
    game.player_ids.append(user_id)
    game.players[user_id] = PlayerInfo(player_id=user_id, role=Roles.VILLAGER)  # El estado del jugador se inicializa cuando comienza la partida
    save_game(game)
    return True

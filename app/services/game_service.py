"""
Módulo de servicios para la gestión de partidas.
Incluye funciones para crear, obtener y listar partidas usando la base de datos JSON.
"""

from app.database import save_game, load_game, load_all_games
from app.models.game import Game, GameStatus
from typing import Optional, List
import random
from app.models.roles import GameRole, RoleInfo

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

def join_game(game_id: str, user) -> bool:
    """Permite que un usuario se una a una partida si está en estado WAITING y hay espacios disponibles."""
    from app.database import load_game, save_game
    game = load_game(game_id)
    if not game:
        return False
    
    # Solo se puede unir si la partida está en estado WAITING
    if game.status != GameStatus.WAITING:
        return False
    
    # Verificar que no haya alcanzado el máximo de jugadores
    if len(game.players) >= game.max_players:
        return False
    
    # Verificar que el usuario no esté ya en la partida
    if any(p.id == user.id for p in game.players):
        return False
    
    # Agregar al usuario a la lista de jugadores
    game.players.append(user)
    save_game(game)
    return True

def assign_roles(game_id: str, user_id: str, is_admin: bool = False) -> Optional[Game]:
    """Asigna roles automáticamente a todos los jugadores de una partida y cambia su estado a STARTED."""
    game = load_game(game_id)
    if not game:
        return None
    
    # Solo el creador o admin pueden iniciar el reparto de roles
    if not is_admin and game.creator_id != user_id:
        return None
    
    # Solo se puede asignar roles si la partida está en estado WAITING
    if game.status != GameStatus.WAITING:
        return None
    
    # Debe haber al menos 10 jugadores para una partida
    num_players = len(game.players)
    if num_players < 10 or num_players > 18:
        return None
    
    # Calcular número de hombres lobo (1 por cada 4 jugadores aproximadamente)
    num_werewolves = max(1, num_players // 3)
    
    # Lista de todos los roles disponibles
    available_roles = []
    
    # Añadir hombres lobo
    for _ in range(num_werewolves):
        available_roles.append(GameRole.WEREWOLF)
    
    # Añadir roles especiales (máximo 1 de cada tipo, según disponibilidad)
    special_roles = [GameRole.SEER, GameRole.WITCH, GameRole.HUNTER, GameRole.CUPID]
    remaining_slots = num_players - num_werewolves
    
    # Asignar roles especiales si hay suficientes jugadores
    for role in special_roles:
        if remaining_slots > 1:  # Siempre dejar al menos 1 aldeano
            available_roles.append(role)
            remaining_slots -= 1
        else:
            break
    
    # El resto son aldeanos
    while len(available_roles) < num_players:
        available_roles.append(GameRole.VILLAGER)
    
    # Mezclar roles aleatoriamente
    random.shuffle(available_roles)
    
    # Asignar roles a jugadores
    game.roles = {}
    for i, player in enumerate(game.players):
        role_info = RoleInfo(
            role=available_roles[i],
            is_alive=True,
            is_revealed=False
        )
        
        # Configurar habilidades específicas según el rol
        if available_roles[i] == GameRole.WITCH:
            role_info.has_healing_potion = True
            role_info.has_poison_potion = True
        elif available_roles[i] == GameRole.CUPID:
            role_info.is_cupid = True
        
        game.roles[player.id] = role_info
    
    # Cambiar estado de la partida a STARTED
    game.status = GameStatus.STARTED
    game.current_round = 1
    
    save_game(game)
    return game

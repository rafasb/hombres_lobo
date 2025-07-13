"""
Módulo de servicios para la gestión del flujo y estados del juego.
Incluye funciones para cambiar estados de partida y asignar roles.
"""

from app.database import save_game, load_game
from app.models.game import Game, GameStatus
from app.models.roles import GameRole, RoleInfo
from typing import Optional
import random


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
        available_roles.append(GameRole.WAREWOLF)
    
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
        elif available_roles[i] == GameRole.SHERIFF:
            role_info.has_double_vote = True
            role_info.can_break_ties = True
        elif available_roles[i] == GameRole.HUNTER:
            role_info.can_revenge_kill = True
            role_info.has_used_revenge = False
        
        game.roles[player.id] = role_info
    
    # Cambiar estado de la partida a STARTED
    game.status = GameStatus.STARTED
    game.current_round = 1
    
    save_game(game)
    return game

def reset_night_actions(game_id: str) -> Optional[Game]:
    """
    Reinicia las acciones nocturnas de todos los jugadores para una nueva noche.
    
    Args:
        game_id: ID de la partida
    
    Returns:
        Game actualizado si fue exitoso, None en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return None
    
    # Reiniciar el estado de acciones nocturnas para todos los jugadores
    for player_id in game.roles:
        game.roles[player_id].has_acted_tonight = False
        game.roles[player_id].target_player_id = None
    
    # Limpiar las acciones nocturnas registradas
    game.night_actions = {}
    
    save_game(game)
    return game

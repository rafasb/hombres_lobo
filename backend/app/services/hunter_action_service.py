from app.database import save_game, load_game
from app.models.game_and_player import Game, Roles
from app.services.user_service import UserService
from typing import Optional, List, Dict

# Funciones para el Cazador

def is_hunter(game_id: str, player_id: str) -> bool:
    """
    Verifica si un jugador es el cazador.
    
    Args:
        game_id: ID de la partida
        player_id: ID del jugador
    
    Returns:
        True si es el cazador, False en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return False
    
    if player_id not in game.players:
        return False
    
    player_role = game.players[player_id]
    return player_role.role == Roles.HUNTER


def can_hunter_revenge(game_id: str, hunter_id: str) -> bool:
    """
    Verifica si el cazador puede usar su habilidad de venganza.
    
    Args:
        game_id: ID de la partida
        hunter_id: ID del cazador
    
    Returns:
        True si puede usar venganza, False en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return False
    
    # Verificar que el jugador existe y es cazador
    if hunter_id not in game.players:
        return False
    
    hunter_role = game.players[hunter_id]
    if hunter_role.role != Roles.HUNTER:
        return False
    
    # El cazador puede vengarse si está muerto pero no ha usado su venganza
    if hunter_role.is_alive:
        return False
    
    # Verificar que no ha usado ya su habilidad de venganza
    if hunter_role.can_revenge_kill is False:
        return False
    
    return True


def hunter_revenge_kill(game_id: str, hunter_id: str, target_id: str) -> Optional[Game]:
    """
    Permite al cazador llevarse a otro jugador cuando muere.
    
    Args:
        game_id: ID de la partida
        hunter_id: ID del cazador
        target_id: ID del jugador objetivo para la venganza
    
    Returns:
        Game actualizado si la acción fue exitosa, None en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return None
    
    # Verificar que puede usar venganza
    if not can_hunter_revenge(game_id, hunter_id):
        return None
    
    # Verificar que el objetivo existe y está vivo
    if target_id not in game.players:
        return None
    
    target_role = game.players[target_id]
    if not target_role.is_alive:
        return None
    
    # No puede vengarse de sí mismo (aunque ya esté muerto)
    if hunter_id == target_id:
        return None
    
    # Marcar al objetivo como muerto
    target_role.is_alive = False
    
    # Marcar que el cazador ya usó su venganza
    hunter_role = game.players[hunter_id]
    hunter_role.can_revenge_kill = True
    hunter_role.target_player_id = target_id
    
    # Guardar la partida
    save_game(game)
    return game


def mark_hunter_as_eliminated(game_id: str, hunter_id: str, eliminated_by: str = "unknown") -> Optional[Game]:
    """
    Marca al cazador como eliminado y activa su habilidad de venganza.
    
    Args:
        game_id: ID de la partida
        hunter_id: ID del cazador
        eliminated_by: Causa de eliminación ("lynching", "warewolf_attack", etc.)
    
    Returns:
        Game actualizado si la acción fue exitosa, None en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return None
    
    # Verificar que es cazador y está vivo
    if hunter_id not in game.players:
        return None
    
    hunter_role = game.players[hunter_id]
    if hunter_role.role != Roles.HUNTER or not hunter_role.is_alive:
        return None
    
    # Marcar como muerto pero con venganza disponible
    hunter_role.is_alive = False
    hunter_role.can_revenge_kill = True
    
    save_game(game)
    return game


def get_hunter_revenge_targets(game_id: str, hunter_id: str) -> List[Dict[str, str]]:
    """
    Obtiene la lista de jugadores que el cazador puede eliminar por venganza.
    
    Args:
        game_id: ID de la partida
        hunter_id: ID del cazador
    
    Returns:
        Lista de jugadores vivos que pueden ser objetivo de venganza
    """
    game = load_game(game_id)
    if not game:
        return []
    
    eligible_targets = []
    
    for player in game.players:
        # Excluir al propio cazador
        if player == hunter_id:
            continue
        
        # Solo incluir jugadores vivos
        if player in game.players:
            role_info = game.players[player]
            if role_info.is_alive:
                eligible_targets.append({
                    "id": player,
                    "username": UserService.get_username_by_id(player)
                })
    
    return eligible_targets


def check_hunter_death_triggers(game_id: str) -> List[str]:
    """
    Verifica si hay cazadores que murieron y necesitan activar su venganza.
    
    Args:
        game_id: ID de la partida
    
    Returns:
        Lista de IDs de cazadores que pueden vengarse
    """
    game = load_game(game_id)
    if not game:
        return []
    
    hunters_needing_revenge = []
    
    for player_id, role_info in game.players.items():
        if (role_info.role == Roles.HUNTER and 
            not role_info.is_alive and
            role_info.can_revenge_kill):
            hunters_needing_revenge.append(player_id)
    
    return hunters_needing_revenge


def auto_eliminate_hunter_target(game_id: str, hunter_id: str) -> Optional[Dict[str, str]]:
    """
    Obtiene información del objetivo del cazador para eliminación automática.
    
    Args:
        game_id: ID de la partida
        hunter_id: ID del cazador
    
    Returns:
        Diccionario con información del objetivo, None si no hay
    """
    game = load_game(game_id)
    if not game:
        return None
    
    if hunter_id not in game.players:
        return None
    
    hunter_role = game.players[hunter_id]
    if (hunter_role.role != Roles.HUNTER or 
        not hunter_role.can_revenge_kill or 
        not hunter_role.target_player_id):
        return None
    
    # Buscar información del objetivo
    target_id = hunter_role.target_player_id
    for player in game.players:
        if player == target_id:
            return {
                "id": target_id,
                "username": UserService.get_username_by_id(player)
            }
    
    return None


def reset_hunter_revenge_state(game_id: str, hunter_id: str) -> bool:
    """
    Reinicia el estado de venganza del cazador (para casos especiales).
    
    Args:
        game_id: ID de la partida
        hunter_id: ID del cazador
    
    Returns:
        True si se reinició correctamente, False en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return False
    
    if hunter_id not in game.players:
        return False
    
    hunter_role = game.players[hunter_id]
    if hunter_role.role != Roles.HUNTER:
        return False
    
    # Reiniciar estado de venganza
    hunter_role.can_revenge_kill = False
    hunter_role.target_player_id = None
    
    save_game(game)
    return True

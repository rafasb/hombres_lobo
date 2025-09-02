from app.database import save_game, load_game
from app.models.game_and_player import Game, Roles, GameStatus
from app.services.user_service import UserService
from typing import Optional, List, Dict, Any
from app.services.warewolf_action_service import get_warewolf_attack_victim

# Funciones para la Bruja

def is_witch(game_id: str, player_id: str) -> bool:
    """
    Verifica si un jugador es la bruja.
    
    Args:
        game_id: ID de la partida
        player_id: ID del jugador
    
    Returns:
        True si es la bruja, False en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return False
    
    if player_id not in game.players:
        return False
    
    player_role = game.players[player_id]
    return player_role.role == Roles.WITCH and player_role.is_alive


def can_witch_heal(game_id: str, witch_id: str) -> bool:
    """
    Verifica si la bruja puede usar su poción de curación.
    
    Args:
        game_id: ID de la partida
        witch_id: ID de la bruja
    
    Returns:
        True si puede curar, False en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return False
    
    # Verificar que la partida esté en fase nocturna
    if game.status != GameStatus.NIGHT:
        return False
    
    # Verificar que es bruja y está viva
    if not is_witch(game_id, witch_id):
        return False
    
    witch_role = game.players[witch_id]
    
    # Verificar que aún tiene la poción de curación
    if not witch_role.has_healing_potion:
        return False
    
    return True


def can_witch_poison(game_id: str, witch_id: str) -> bool:
    """
    Verifica si la bruja puede usar su poción de veneno.
    
    Args:
        game_id: ID de la partida
        witch_id: ID de la bruja
    
    Returns:
        True si puede envenenar, False en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return False
    
    # Verificar que la partida esté en fase nocturna
    if game.status != GameStatus.NIGHT:
        return False
    
    # Verificar que es bruja y está viva
    if not is_witch(game_id, witch_id):
        return False
    
    witch_role = game.players[witch_id]
    
    # Verificar que aún tiene la poción de veneno
    if not witch_role.has_poison_potion:
        return False
    
    return True



def witch_heal_victim(game_id: str, witch_id: str, victim_id: str) -> Optional[Game]:
    """
    Permite a la bruja usar su poción de curación para salvar a la víctima de los lobos.
    
    Args:
        game_id: ID de la partida
        witch_id: ID de la bruja
        victim_id: ID del jugador a curar (debe ser la víctima del ataque)
    
    Returns:
        Game actualizado si la acción fue exitosa, None en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return None
    
    # Verificar que puede curar
    if not can_witch_heal(game_id, witch_id):
        return None
    
    # Verificar que el objetivo es realmente la víctima del ataque de lobos
    attack_victim = get_warewolf_attack_victim(game_id)
    if not attack_victim or attack_victim != victim_id:
        return None
    
    # Verificar que la víctima existe
    if victim_id not in game.players:
        return None
    
    # Marcar que la bruja usó su poción de curación
    witch_role = game.players[witch_id]
    witch_role.has_healing_potion = False
    
    # Registrar la acción de curación en night_actions
    if "witch_heal" not in game.night_actions:
        game.night_actions["witch_heal"] = {}
    game.night_actions["witch_heal"][witch_id] = victim_id
    
    save_game(game)
    return game


def witch_poison_player(game_id: str, witch_id: str, target_id: str) -> Optional[Game]:
    """
    Permite a la bruja usar su poción de veneno para eliminar a un jugador.
    
    Args:
        game_id: ID de la partida
        witch_id: ID de la bruja
        target_id: ID del jugador a envenenar
    
    Returns:
        Game actualizado si la acción fue exitosa, None en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return None
    
    # Verificar que puede envenenar
    if not can_witch_poison(game_id, witch_id):
        return None
    
    # Verificar que el objetivo existe y está vivo
    if target_id not in game.players:
        return None
    
    target_role = game.players[target_id]
    if not target_role.is_alive:
        return None
    
    # La bruja puede envenenarse a sí misma si quiere
    # (no hay restricción en las reglas tradicionales)
    
    # Marcar que la bruja usó su poción de veneno
    witch_role = game.players[witch_id]
    witch_role.has_poison_potion = False
    
    # Registrar la acción de envenenamiento en night_actions
    if "witch_poison" not in game.night_actions:
        game.night_actions["witch_poison"] = {}
    game.night_actions["witch_poison"][witch_id] = target_id
    
    save_game(game)
    return game


def get_witch_night_info(game_id: str, witch_id: str) -> Dict[str, Any]:
    """
    Obtiene información de la noche para la bruja (quién fue atacado, qué pociones tiene).
    
    Args:
        game_id: ID de la partida
        witch_id: ID de la bruja
    
    Returns:
        Diccionario con información de la noche para la bruja
    """
    game = load_game(game_id)
    if not game:
        return {}
    
    # Verificar que es bruja
    if not is_witch(game_id, witch_id):
        return {}
    
    witch_role = game.players[witch_id]
    
    # Obtener información del ataque de lobos
    attack_victim_id = get_warewolf_attack_victim(game_id)
    attack_victim_username = None
    
    if attack_victim_id:
        for player in game.players:
            if player == attack_victim_id:
                attack_victim_username = UserService.get_username_by_id(player)
                break
    
    return {
        "attacked_player_id": attack_victim_id,
        "attacked_username": attack_victim_username,
        "can_heal": witch_role.has_healing_potion or False,
        "can_poison": witch_role.has_poison_potion or False,
        "has_healing_potion": witch_role.has_healing_potion or False,
        "has_poison_potion": witch_role.has_poison_potion or False
    }


def get_witch_poison_targets(game_id: str, witch_id: str) -> List[Dict[str, str]]:
    """
    Obtiene la lista de jugadores que la bruja puede envenenar.
    
    Args:
        game_id: ID de la partida
        witch_id: ID de la bruja
    
    Returns:
        Lista de jugadores vivos que pueden ser envenenados
    """
    game = load_game(game_id)
    if not game:
        return []
    
    eligible_targets = []
    
    for player in game.players:
        # Incluir todos los jugadores vivos (incluso la bruja puede envenenarse)
        if player in game.players:
            role_info = game.players[player]
            if role_info.is_alive:
                eligible_targets.append({
                    "id": player,
                    "username": UserService.get_username_by_id(player)
                })
    
    return eligible_targets


def process_witch_night_actions(game_id: str) -> Dict[str, List[str]]:
    """
    Procesa las acciones nocturnas de la bruja y devuelve los resultados.
    
    Args:
        game_id: ID de la partida
    
    Returns:
        Diccionario con listas de jugadores curados y envenenados
    """
    game = load_game(game_id)
    if not game:
        return {"healed": [], "poisoned": []}
    
    healed_players = []
    poisoned_players = []
    
    # Procesar curaciones
    if "witch_heal" in game.night_actions:
        for witch_id, victim_id in game.night_actions["witch_heal"].items():
            healed_players.append(victim_id)
    
    # Procesar envenenamientos
    if "witch_poison" in game.night_actions:
        for witch_id, target_id in game.night_actions["witch_poison"].items():
            # Marcar al jugador como muerto por veneno
            if target_id in game.players:
                game.players[target_id].is_alive = False
            poisoned_players.append(target_id)
    
    save_game(game)
    
    return {
        "healed": healed_players,
        "poisoned": poisoned_players
    }


def reset_witch_night_actions(game_id: str) -> bool:
    """
    Reinicia las acciones nocturnas de la bruja para una nueva noche.
    
    Args:
        game_id: ID de la partida
    
    Returns:
        True si se reiniciaron correctamente, False en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return False
    
    # Limpiar acciones de bruja de la noche anterior
    if "witch_heal" in game.night_actions:
        game.night_actions["witch_heal"].clear()
    if "witch_poison" in game.night_actions:
        game.night_actions["witch_poison"].clear()
    
    save_game(game)
    return True


def initialize_witch_potions(game_id: str, witch_id: str) -> bool:
    """
    Inicializa las pociones de la bruja al comienzo del juego.
    
    Args:
        game_id: ID de la partida
        witch_id: ID de la bruja
    
    Returns:
        True si se inicializaron correctamente, False en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return False
    
    if witch_id not in game.players:
        return False
    
    witch_role = game.players[witch_id]
    if witch_role.role != Roles.WITCH:
        return False
    
    # Inicializar pociones
    witch_role.has_healing_potion = True
    witch_role.has_poison_potion = True
    
    save_game(game)
    return True


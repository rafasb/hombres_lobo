from app.database import save_game, load_game
from app.models.game_and_player import Game, Roles, GameStatus
from app.services.user_service import UserService
from typing import Optional, List, Dict, Any

# Funciones para El Niño Salvaje

def is_wild_child(game_id: str, player_id: str) -> bool:
    """
    Verifica si un jugador es el Niño Salvaje.
    
    Args:
        game_id: ID de la partida
        player_id: ID del jugador
    
    Returns:
        True si es el Niño Salvaje, False en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return False
    
    if player_id not in game.players:
        return False
    
    player_role = game.players[player_id]
    return player_role.role == Roles.WILD_CHILD and player_role.is_alive


def can_wild_child_choose_model(game_id: str, wild_child_id: str) -> bool:
    """
    Verifica si el Niño Salvaje puede elegir un modelo.
    
    Args:
        game_id: ID de la partida
        wild_child_id: ID del Niño Salvaje
    
    Returns:
        True si puede elegir modelo, False en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return False
    
    # Verificar que es Niño Salvaje y está vivo
    if not is_wild_child(game_id, wild_child_id):
        return False
    
    wild_child_role = game.players[wild_child_id]
    
    # Solo puede elegir modelo si no ha elegido uno aún
    if wild_child_role.model_player_id:
        return False
    
    # Solo puede elegir en la primera noche
    return game.current_round <= 1 and game.status == GameStatus.NIGHT


def get_available_models_for_wild_child(game_id: str, wild_child_id: str) -> List[Dict[str, str]]:
    """
    Obtiene la lista de jugadores que pueden ser modelo del Niño Salvaje.
    
    Args:
        game_id: ID de la partida
        wild_child_id: ID del Niño Salvaje
    
    Returns:
        Lista de jugadores que pueden ser modelo
    """
    game = load_game(game_id)
    if not game:
        return []
    
    available_models = []
    
    for player in game.players:
        # El modelo puede ser cualquier jugador vivo excepto él mismo
        if player != wild_child_id and player in game.players:
            role_info = game.players[player]
            if role_info.is_alive:
                available_models.append({
                    "id": player,
                    "username": UserService.get_username_by_id(player)
                })
    
    return available_models


def wild_child_choose_model(game_id: str, wild_child_id: str, model_player_id: str) -> Optional[Game]:
    """
    Permite al Niño Salvaje elegir su jugador modelo.
    
    Args:
        game_id: ID de la partida
        wild_child_id: ID del Niño Salvaje
        model_player_id: ID del jugador modelo elegido
    
    Returns:
        Game actualizado si la elección fue exitosa, None en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return None
    
    # Verificar que puede elegir modelo
    if not can_wild_child_choose_model(game_id, wild_child_id):
        return None
    
    # Verificar que el modelo existe y está vivo
    if model_player_id not in game.players:
        return None
    
    model_role = game.players[model_player_id]
    if not model_role.is_alive:
        return None
    
    # El modelo no puede ser él mismo
    if model_player_id == wild_child_id:
        return None
    
    # Asignar el modelo
    wild_child_role = game.players[wild_child_id]
    wild_child_role.model_player_id = model_player_id
    wild_child_role.has_transformed = False
    
    # Registrar la acción en night_actions
    if "wild_child_model" not in game.night_actions:
        game.night_actions["wild_child_model"] = {}
    game.night_actions["wild_child_model"][wild_child_id] = model_player_id
    
    save_game(game)
    return game


def get_wild_child_status(game_id: str, wild_child_id: str) -> Dict[str, Any]:
    """
    Obtiene el estado actual del Niño Salvaje.
    
    Args:
        game_id: ID de la partida
        wild_child_id: ID del Niño Salvaje
    
    Returns:
        Diccionario con el estado del Niño Salvaje
    """
    game = load_game(game_id)
    if not game:
        return {}
    
    if wild_child_id not in game.players:
        return {}
    
    wild_child_role = game.players[wild_child_id]
    
    # Verificar que era originalmente Niño Salvaje (puede haber cambiado a WAREWOLF)
    if wild_child_role.role not in [Roles.WILD_CHILD, Roles.WAREWOLF]:
        return {}
    
    model_username = None
    if wild_child_role.model_player_id:
        for player in game.players:
            if player == wild_child_role.model_player_id:
                model_username = UserService.get_username_by_id(player)
                break
    
    current_role = "warewolf" if wild_child_role.has_transformed else "wild_child"
    
    return {
        "has_model": bool(wild_child_role.model_player_id),
        "model_player_id": wild_child_role.model_player_id,
        "model_username": model_username,
        "is_transformed": wild_child_role.has_transformed or False,
        "current_role": current_role
    }


def check_wild_child_transformation(game_id: str, dead_player_id: str) -> List[Dict[str, Any]]:
    """
    Verifica si algún Niño Salvaje debe transformarse debido a la muerte de su modelo.
    
    Args:
        game_id: ID de la partida
        dead_player_id: ID del jugador que acaba de morir
    
    Returns:
        Lista de transformaciones que ocurrieron
    """
    game = load_game(game_id)
    if not game:
        return []
    
    transformations = []
    
    # Buscar todos los Niños Salvajes que tengan como modelo al jugador muerto
    for player_id, role_info in game.players.items():
        if (role_info.role == Roles.WILD_CHILD and 
            role_info.is_alive and 
            role_info.model_player_id == dead_player_id and
            not role_info.has_transformed):
            
            # Transformar al Niño Salvaje en Hombre Lobo
            role_info.has_transformed = True
            role_info.role = Roles.WAREWOLF
            
            # Obtener nombre del jugador
            player_username = None
            for player in game.players:
                if player == player_id:
                    player_username = UserService.get_username_by_id(player)
                    break
            
            transformations.append({
                "wild_child_id": player_id,
                "wild_child_username": player_username,
                "model_id": dead_player_id,
                "reason": f"Su modelo {dead_player_id} ha muerto"
            })
    
    if transformations:
        save_game(game)
    
    return transformations


def notify_werewolves_of_new_member(game_id: str, new_werewolf_id: str) -> List[str]:
    """
    Obtiene la lista de hombres lobo existentes para notificarles del nuevo miembro.
    
    Args:
        game_id: ID de la partida
        new_werewolf_id: ID del nuevo hombre lobo (Niño Salvaje transformado)
    
    Returns:
        Lista de IDs de hombres lobo existentes
    """
    game = load_game(game_id)
    if not game:
        return []
    
    existing_werewolves = []
    
    for player_id, role_info in game.players.items():
        if (role_info.role == Roles.WAREWOLF and 
            role_info.is_alive and 
            player_id != new_werewolf_id):
            existing_werewolves.append(player_id)
    
    return existing_werewolves


def get_wild_child_transformation_info(game_id: str, wild_child_id: str) -> Dict[str, Any]:
    """
    Obtiene información sobre la transformación del Niño Salvaje.
    
    Args:
        game_id: ID de la partida
        wild_child_id: ID del Niño Salvaje
    
    Returns:
        Información sobre su transformación o estado actual
    """
    game = load_game(game_id)
    if not game:
        return {}
    
    if wild_child_id not in game.players:
        return {}
    
    wild_child_role = game.players[wild_child_id]
    
    # Si no era Niño Salvaje originalmente, no aplica
    if wild_child_role.role not in [Roles.WILD_CHILD, Roles.WAREWOLF]:
        return {}
    
    model_username = None
    model_is_alive = False
    
    if wild_child_role.model_player_id:
        for player in game.players:
            if player == wild_child_role.model_player_id:
                model_username = UserService.get_username_by_id(player)
                if wild_child_role.model_player_id in game.players:
                    model_is_alive = game.players[wild_child_role.model_player_id].is_alive
                break
    
    return {
        "has_model": bool(wild_child_role.model_player_id),
        "model_player_id": wild_child_role.model_player_id,
        "model_username": model_username,
        "model_is_alive": model_is_alive,
        "is_transformed": wild_child_role.has_transformed or False,
        "current_role": wild_child_role.role.value,
        "original_role": "wild_child"
    }


def reset_wild_child_night_actions(game_id: str) -> bool:
    """
    Reinicia las acciones nocturnas del Niño Salvaje para una nueva noche.
    
    Args:
        game_id: ID de la partida
    
    Returns:
        True si se reiniciaron correctamente, False en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return False
    
    # Limpiar acciones del Niño Salvaje de la noche anterior
    if "wild_child_model" in game.night_actions:
        game.night_actions["wild_child_model"].clear()
    
    save_game(game)
    return True


def initialize_wild_child(game_id: str, wild_child_id: str) -> bool:
    """
    Inicializa al Niño Salvaje al comienzo del juego.
    
    Args:
        game_id: ID de la partida
        wild_child_id: ID del Niño Salvaje
    
    Returns:
        True si se inicializó correctamente, False en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return False
    
    if wild_child_id not in game.players:
        return False
    
    wild_child_role = game.players[wild_child_id]
    if wild_child_role.role != Roles.WILD_CHILD:
        return False
    
    # Inicializar estado
    wild_child_role.model_player_id = None
    wild_child_role.has_transformed = False
    
    save_game(game)
    return True


def process_wild_child_death_check(game_id: str) -> List[Dict[str, Any]]:
    """
    Procesa todas las muertes para verificar transformaciones de Niños Salvajes.
    Debe llamarse después de procesar todas las muertes de una ronda.
    
    Args:
        game_id: ID de la partida
    
    Returns:
        Lista de todas las transformaciones que ocurrieron
    """
    game = load_game(game_id)
    if not game:
        return []
    
    all_transformations = []
    
    # Verificar todos los jugadores muertos en esta ronda
    for player_id, role_info in game.players.items():
        if not role_info.is_alive:
            # Verificar si la muerte de este jugador causa transformaciones
            transformations = check_wild_child_transformation(game_id, player_id)
            all_transformations.extend(transformations)
    
    return all_transformations


def simulate_player_death(game_id: str, player_id: str) -> bool:
    """
    Marca a un jugador como muerto (función auxiliar para testing y procesamiento de muertes).
    
    Args:
        game_id: ID de la partida
        player_id: ID del jugador que muere
    
    Returns:
        True si se marcó como muerto, False en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return False
    
    if player_id not in game.players:
        return False
    
    game.players[player_id].is_alive = False
    save_game(game)
    return True


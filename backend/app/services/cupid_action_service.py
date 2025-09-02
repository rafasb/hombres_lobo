from app.database import save_game, load_game
from app.models.game_and_player import Game, Roles, GameStatus
from app.services.user_service import UserService
from typing import Optional, List, Dict, Any

# === FUNCIONES DE CUPIDO ===

def is_cupid(game_id: str, player_id: str) -> bool:
    """
    Verifica si un jugador es Cupido.
    
    Args:
        game_id: ID de la partida
        player_id: ID del jugador
    
    Returns:
        True si es Cupido, False en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return False
    
    if player_id not in game.players:
        return False
    
    return game.players[player_id].role == Roles.CUPID


def can_cupid_choose_lovers(game_id: str, cupid_id: str) -> bool:
    """
    Verifica si Cupido puede elegir enamorados.
    
    Args:
        game_id: ID de la partida
        cupid_id: ID de Cupido
    
    Returns:
        True si puede elegir, False en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return False
    
    # Verificar que es Cupido
    if not is_cupid(game_id, cupid_id):
        return False
    
    # Verificar que está vivo
    if not game.players[cupid_id].is_alive:
        return False
    
    # Solo puede elegir en la primera noche
    if game.current_round != 1:
        return False
    
    # Verificar que la partida está en fase de noche
    if game.status != GameStatus.NIGHT:
        return False
    
    # Verificar que no ha elegido enamorados ya
    cupid_actions = game.night_actions.get("cupid_lovers", {})
    if cupid_id in cupid_actions:
        return False
    
    return True


def get_cupid_available_targets(game_id: str, cupid_id: str) -> List[Dict[str, str]]:
    """
    Obtiene la lista de jugadores disponibles para enamorar.
    
    Args:
        game_id: ID de la partida
        cupid_id: ID de Cupido
    
    Returns:
        Lista de jugadores disponibles
    """
    game = load_game(game_id)
    if not game:
        return []
    
    available_targets = []
    
    # Todos los jugadores vivos pueden ser enamorados
    for player in game.players:
        if (player in game.players and 
            game.players[player].is_alive):
            available_targets.append({
                "id": player,
                "username": UserService.get_username_by_id(player)
            })
    
    return available_targets


def cupid_choose_lovers(game_id: str, cupid_id: str, lover1_id: str, lover2_id: str) -> Optional[Game]:
    """
    Permite a Cupido elegir a dos jugadores como enamorados.
    
    Args:
        game_id: ID de la partida
        cupid_id: ID de Cupido
        lover1_id: ID del primer enamorado
        lover2_id: ID del segundo enamorado
    
    Returns:
        Game actualizado si la elección fue exitosa, None en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return None
    
    # Verificar que puede elegir
    if not can_cupid_choose_lovers(game_id, cupid_id):
        return None
    
    # Verificar que los enamorados existen y están vivos
    if lover1_id not in game.players or lover2_id not in game.players:
        return None
    
    if not game.players[lover1_id].is_alive or not game.players[lover2_id].is_alive:
        return None
    
    # Los enamorados deben ser diferentes
    if lover1_id == lover2_id:
        return None
    
    # Marcar a los jugadores como enamorados
    game.players[lover1_id].lover_partner_id = lover2_id
    
    game.players[lover2_id].lover_partner_id = lover1_id
    
    # Marcar a Cupido como que ya eligió
    game.players[cupid_id].has_cupid_action = False
    
    # Registrar la acción en night_actions
    if "cupid_lovers" not in game.night_actions:
        game.night_actions["cupid_lovers"] = {}
    # Almacenamos como "lover1_id:lover2_id"
    game.night_actions["cupid_lovers"][cupid_id] = f"{lover1_id}:{lover2_id}"
    
    save_game(game)
    return game


def get_cupid_status(game_id: str, cupid_id: str) -> Dict[str, Any]:
    """
    Obtiene el estado actual de Cupido.
    
    Args:
        game_id: ID de la partida
        cupid_id: ID de Cupido
    
    Returns:
        Diccionario con el estado de Cupido
    """
    game = load_game(game_id)
    if not game:
        return {
            "has_chosen_lovers": False,
            "lover1_id": None,
            "lover1_username": None,
            "lover2_id": None,
            "lover2_username": None
        }
    
    # Verificar si ya eligió enamorados
    cupid_actions = game.night_actions.get("cupid_lovers", {})
    has_chosen = cupid_id in cupid_actions
    
    lover1_id = None
    lover1_username = None
    lover2_id = None
    lover2_username = None
    
    if has_chosen:
        lovers_string = cupid_actions[cupid_id]
        # Parsear "lover1_id:lover2_id"
        lovers_parts = lovers_string.split(":")
        if len(lovers_parts) == 2:
            lover1_id = lovers_parts[0]
            lover2_id = lovers_parts[1]
            
            # Obtener nombres de usuario
            for player in game.players:
                if player == lover1_id:
                    lover1_username = UserService.get_username_by_id(player)
                elif player == lover2_id:
                    lover2_username = UserService.get_username_by_id(player)
    
    return {
        "has_chosen_lovers": has_chosen,
        "lover1_id": lover1_id,
        "lover1_username": lover1_username,
        "lover2_id": lover2_id,
        "lover2_username": lover2_username
    }


def get_lovers_status(game_id: str, player_id: str) -> Dict[str, Any]:
    """
    Obtiene el estado de los enamorados para un jugador.
    
    Args:
        game_id: ID de la partida
        player_id: ID del jugador
    
    Returns:
        Diccionario con el estado de enamorado
    """
    game = load_game(game_id)
    if not game:
        return {
            "is_lover": False,
            "partner_id": None,
            "partner_username": None,
            "both_alive": False
        }
    
    if player_id not in game.players:
        return {
            "is_lover": False,
            "partner_id": None,
            "partner_username": None,
            "both_alive": False
        }
    
    role_info = game.players[player_id]
    
    if role_info.lover_partner_id == '':
        return {
            "is_lover": False,
            "partner_id": None,
            "partner_username": None,
            "both_alive": False
        }
    
    partner_id = role_info.lover_partner_id
    partner_username = None
    both_alive = False
    
    if partner_id and partner_id in game.players:
        # Obtener nombre del compañero
        for player in game.players:
            if player == partner_id:
                partner_username = UserService.get_username_by_id(player)
                break
        
        # Verificar si ambos están vivos
        both_alive = role_info.is_alive and game.players[partner_id].is_alive
    
    return {
        "is_lover": True,
        "partner_id": partner_id,
        "partner_username": partner_username,
        "both_alive": both_alive
    }


def check_lovers_death(game_id: str, dead_player_id: str) -> List[str]:
    """
    Verifica si un enamorado debe morir cuando muere su pareja.
    
    Args:
        game_id: ID de la partida
        dead_player_id: ID del jugador que acaba de morir
    
    Returns:
        Lista con IDs de enamorados que mueren por la pérdida de su pareja
    """
    game = load_game(game_id)
    if not game:
        return []
    
    deaths_by_love = []
    
    # Verificar si el muerto era enamorado
    if (dead_player_id in game.players and
        game.players[dead_player_id].lover_partner_id != ''):
        
        partner_id = game.players[dead_player_id].lover_partner_id
        
        # Si el compañero aún está vivo, muere de pena
        if (partner_id in game.players and 
            game.players[partner_id].is_alive):
            
            game.players[partner_id].is_alive = False
            deaths_by_love.append(partner_id)
    
    if deaths_by_love:
        save_game(game)
    
    return deaths_by_love


def check_lovers_victory_condition(game_id: str) -> Optional[Dict[str, Any]]:
    """
    Verifica si los enamorados han ganado la partida.
    
    Args:
        game_id: ID de la partida
    
    Returns:
        Información de victoria si los enamorados ganaron, None en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return None
    
    # Contar jugadores vivos
    alive_players = []
    for player_id, role_info in game.players.items():
        if role_info.is_alive:
            alive_players.append(player_id)
    
    # Si solo quedan 2 jugadores vivos, verificar si son enamorados
    if len(alive_players) == 2:
        player1_id = alive_players[0]
        player2_id = alive_players[1]
        
        # Verificar si ambos son enamorados y están enlazados entre sí
        if (game.players[player1_id].lover_partner_id == player2_id and
            game.players[player2_id].lover_partner_id == player1_id):
            
            # Obtener nombres de usuario
            player1_username = None
            player2_username = None
            for player in game.players:
                if player == player1_id:
                    player1_username = UserService.get_username_by_id(player)
                elif player == player2_id:
                    player2_username = UserService.get_username_by_id(player)
            
            return {
                "victory_type": "lovers",
                "winners": [
                    {"id": player1_id, "username": player1_username},
                    {"id": player2_id, "username": player2_username}
                ],
                "message": "Los enamorados han ganado la partida"
            }
    
    return None


def initialize_cupid_night_actions(game_id: str, cupid_id: str) -> bool:
    """
    Inicializa las acciones nocturnas de Cupido.
    
    Args:
        game_id: ID de la partida
        cupid_id: ID de Cupido
    
    Returns:
        True si se inicializó correctamente, False en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return False
    
    # Verificar que es Cupido
    if not is_cupid(game_id, cupid_id):
        return False
    
    # Marcar como Cupido
    game.players[cupid_id].has_cupid_action = True
    
    # Inicializar acciones nocturnas si no existen
    if "cupid_lovers" not in game.night_actions:
        game.night_actions["cupid_lovers"] = {}
    
    save_game(game)
    return True


def reset_cupid_night_actions(game_id: str) -> bool:
    """
    Reinicia las acciones nocturnas de Cupido.
    
    Args:
        game_id: ID de la partida
    
    Returns:
        True si se reinició correctamente, False en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return False
    
    # Limpiar acciones de Cupido
    if "cupid_lovers" in game.night_actions:
        game.night_actions["cupid_lovers"] = {}
    
    save_game(game)
    return True



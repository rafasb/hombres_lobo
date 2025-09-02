"""
Módulo de servicios para las acciones de los jugadores durante las partidas.
Incluye funciones para que los jugadores realicen sus acciones nocturnas específicas según su rol.
"""

from app.database import save_game, load_game
from app.models.game_and_player import Game, GameStatus, Roles
from app.services.user_service import UserService
from typing import Optional, List, Dict, Any


def warewolf_attack(game_id: str, attacker_id: str, target_id: str) -> Optional[Game]:
    """
    Permite a un hombre lobo seleccionar a un aldeano para devorar durante la fase nocturna.
    
    Args:
        game_id: ID de la partida
        attacker_id: ID del jugador hombre lobo que realiza el ataque
        target_id: ID del jugador objetivo (aldeano a devorar)
    
    Returns:
        Game actualizado si la acción fue exitosa, None en caso contrario
    """
    game: Game | None = load_game(game_id)
    if not game:
        return None
    
    # Verificar que la partida esté en fase nocturna
    if game.status != GameStatus.NIGHT:
        return None
    
    # Verificar que el atacante existe y está vivo
    if attacker_id not in game.players:
        return None
    
    attacker_role = game.players[attacker_id]
    if not attacker_role.is_alive:
        return None
    
    # Verificar que el atacante es un hombre lobo
    if attacker_role.role != Roles.WAREWOLF:
        return None
    
    # Verificar que el objetivo existe y está vivo
    if target_id not in game.players:
        return None
    
    target_role = game.players[target_id]
    if not target_role.is_alive:
        return None
    
    # Verificar que el objetivo no es un hombre lobo (no pueden atacarse entre ellos)
    if target_role.role == Roles.WAREWOLF:
        return None
    
    # Verificar que el hombre lobo no ha actuado ya esta noche
    if attacker_role.has_acted_tonight:
        return None
    
    # Registrar la acción del hombre lobo
    game.players[attacker_id].has_acted_tonight = True
    game.players[attacker_id].target_player_id = target_id
    
    # Registrar el voto de ataque del hombre lobo
    if 'warewolf_attacks' not in game.night_actions:
        game.night_actions['warewolf_attacks'] = {}
    
    game.night_actions['warewolf_attacks'][attacker_id] = target_id
    
    save_game(game)
    return game


def get_warewolf_attack_consensus(game_id: str) -> Optional[str]:
    """
    Determina si los hombres lobo han llegado a un consenso sobre a quién atacar.
    
    Args:
        game_id: ID de la partida
    
    Returns:
        ID del jugador objetivo si hay consenso, None en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return None
    
    if 'warewolf_attacks' not in game.night_actions:
        return None
    
    # Obtener todos los hombres lobo vivos
    warewolves = [
        player_id for player_id, role_info in game.players.items()
        if role_info.role == Roles.WAREWOLF and role_info.is_alive
    ]
    
    # Obtener votos de ataque
    attack_votes = game.night_actions['warewolf_attacks']
    
    # Verificar si todos los hombres lobo han votado
    warewolf_votes = {ww_id: attack_votes.get(ww_id) for ww_id in warewolves if ww_id in attack_votes}
    
    if len(warewolf_votes) != len(warewolves):
        return None  # No todos han votado aún
    
    # Contar votos por objetivo
    vote_counts = {}
    for target_id in warewolf_votes.values():
        vote_counts[target_id] = vote_counts.get(target_id, 0) + 1
    
    # Encontrar el objetivo con más votos
    if not vote_counts:
        return None
    
    max_votes = max(vote_counts.values())
    targets_with_max_votes = [target for target, votes in vote_counts.items() if votes == max_votes]
    
    # Si hay empate, no hay consenso (podrían implementarse reglas de desempate)
    if len(targets_with_max_votes) > 1:
        return None
    
    return targets_with_max_votes[0]


def get_alive_players(game_id: str, exclude: str ='') -> List[Dict[str, str]]:
    """
    Obtiene la lista de jugadores vivos en una partida.
    
    Args:
        game_id: ID de la partida
    
    Returns:
        Lista de diccionarios con id y nombre de jugadores vivos
    """
    game = load_game(game_id)
    if not game:
        return []
    
    alive_players = []
    for player in game.players:
        if player in game.players and game.players[player].is_alive and player != exclude:
            alive_players.append({
                "id": player,
                "username": UserService.get_username_by_id(player)
            })
    
    return alive_players


def get_non_warewolf_players(game_id: str) -> List[Dict[str, str]]:
    """
    Obtiene la lista de jugadores vivos que no son hombres lobo (objetivos válidos para ataque).
    
    Args:
        game_id: ID de la partida
    
    Returns:
        Lista de diccionarios con id y nombre de jugadores que no son hombres lobo
    """
    game = load_game(game_id)
    if not game:
        return []
    
    valid_targets = []
    for player in game.players:
        if (player in game.players and 
            game.players[player].is_alive and 
            game.players[player].role != Roles.WAREWOLF):
            valid_targets.append({
                "id": player,
                "username": UserService.get_username_by_id(player)
            })
    
    return valid_targets


def can_warewolf_act(game_id: str, player_id: str) -> bool:
    """
    Verifica si un hombre lobo puede realizar una acción nocturna.
    
    Args:
        game_id: ID de la partida
        player_id: ID del jugador hombre lobo
    
    Returns:
        True si puede actuar, False en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return False
    
    # Verificar que la partida esté en fase nocturna
    if game.status != GameStatus.NIGHT:
        return False
    
    # Verificar que el jugador existe y está vivo
    if player_id not in game.players:
        return False
    
    player_role = game.players[player_id]
    if not player_role.is_alive:
        return False
    
    # Verificar que es un hombre lobo
    if player_role.role != Roles.WAREWOLF:
        return False
    
    # Verificar que no ha actuado esta noche
    if player_role.has_acted_tonight:
        return False
    
    return True


def day_vote(game_id: str, voter_id: str, target_id: str) -> Optional[Game]:
    """
    Permite a un jugador vivo votar para eliminar a otro jugador durante la fase diurna.
    
    Args:
        game_id: ID de la partida
        voter_id: ID del jugador que vota
        target_id: ID del jugador objetivo a eliminar
    
    Returns:
        Game actualizado si la acción fue exitosa, None en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return None
    
    # Verificar que la partida esté en fase diurna
    if game.status != GameStatus.DAY:
        return None
    
    # Verificar que el votante existe y está vivo
    if voter_id not in game.players:
        return None
    
    voter_role = game.players[voter_id]
    if not voter_role.is_alive:
        return None
    
    # Verificar que el objetivo existe y está vivo
    if target_id not in game.players:
        return None
    
    target_role = game.players[target_id]
    if not target_role.is_alive:
        return None
    
    # No se puede votar por uno mismo
    if voter_id == target_id:
        return None
    
    # Registrar el voto (sobrescribir si ya había votado)
    game.day_votes[voter_id] = target_id
    
    save_game(game)
    return game


def get_day_vote_counts(game_id: str) -> List[Dict[str, Any]]:
    """
    Obtiene el recuento actual de votos diurnos.
    
    Args:
        game_id: ID de la partida
    
    Returns:
        Lista con el recuento de votos por jugador
    """
    game = load_game(game_id)
    if not game:
        return []
    
    # Contar votos por objetivo
    vote_counts = {}
    for target_id in game.day_votes.values():
        vote_counts[target_id] = vote_counts.get(target_id, 0) + 1
    
    # Crear lista con información de jugadores y sus votos
    vote_results = []
    for player in game.players:
        if player in game.players and game.players[player].is_alive:
            count = vote_counts.get(player, 0)
            vote_results.append({
                "player_id": player,
                "username": UserService.get_username_by_id(player),
                "vote_count": count
            })
    
    # Ordenar por número de votos (descendente)
    vote_results.sort(key=lambda x: x["vote_count"], reverse=True)
    
    return vote_results


def can_player_vote(game_id: str, player_id: str) -> bool:
    """
    Verifica si un jugador puede votar durante la fase diurna.
    
    Args:
        game_id: ID de la partida
        player_id: ID del jugador
    
    Returns:
        True si puede votar, False en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return False
    
    # Verificar que la partida esté en fase diurna
    if game.status != GameStatus.DAY:
        return False
    
    # Verificar que el jugador existe y está vivo
    if player_id not in game.players:
        return False
    
    player_role = game.players[player_id]
    if not player_role.is_alive:
        return False
    
    return True


def get_voting_eligible_players(game_id: str) -> List[Dict[str, str]]:
    """
    Obtiene la lista de jugadores vivos que pueden ser votados para eliminación.
    
    Args:
        game_id: ID de la partida
    
    Returns:
        Lista de diccionarios con id y nombre de jugadores vivos
    """
    game = load_game(game_id)
    if not game:
        return []
    
    eligible_players = []
    for player in game.players:
        if player in game.players and game.players[player].is_alive:
            eligible_players.append({
                "id": player,
                "username": UserService.get_username_by_id(player) 
            })
    
    return eligible_players


def get_player_vote(game_id: str, player_id: str) -> Optional[str]:
    """
    Obtiene el voto actual de un jugador específico.
    
    Args:
        game_id: ID de la partida
        player_id: ID del jugador
    
    Returns:
        ID del jugador votado o None si no ha votado
    """
    game = load_game(game_id)
    if not game:
        return None
    
    return game.day_votes.get(player_id)


def reset_day_votes(game_id: str) -> Optional[Game]:
    """
    Reinicia los votos diurnos para una nueva fase de votación.
    
    Args:
        game_id: ID de la partida
    
    Returns:
        Game actualizado si fue exitoso, None en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return None
    
    # Limpiar los votos diurnos
    game.day_votes = {}
    
    save_game(game)
    return game


def get_voting_summary(game_id: str) -> Dict[str, Any]:
    """
    Obtiene un resumen completo de la votación actual.
    
    Args:
        game_id: ID de la partida
    
    Returns:
        Diccionario con resumen de votación
    """
    game = load_game(game_id)
    if not game:
        return {}
    
    # Contar jugadores vivos
    alive_players = [p for p in game.players if p in game.players and game.players[p].is_alive]
    total_players = len(alive_players)
    total_votes = len(game.day_votes)
    
    # Obtener recuentos de votos
    vote_counts = get_day_vote_counts(game_id)
    
    return {
        "total_players": total_players,
        "total_votes": total_votes,
        "vote_counts": vote_counts,
        "voting_complete": total_votes >= total_players,
        "game_status": game.status.value
    }


# Funciones para la Vidente


def is_valid_target(game: Game, target_id: str) -> bool:
    if target_id not in game.players:
        return False
    target_role = game.players[target_id]
    return target_role.is_alive

def player_name(game: Game, player_id: str) -> Optional[str]:
    if player_id not in game.players:
        return None
    return UserService.get_username_by_id(player_id)




"""
Módulo de servicios para las acciones de los jugadores durante las partidas.
Incluye funciones para que los jugadores realicen sus acciones nocturnas específicas según su rol.
"""

from app.database import save_game, load_game
from app.models.game_and_roles import Game, GameStatus, GameRole
from typing import Optional, List, Dict


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
    game = load_game(game_id)
    if not game:
        return None
    
    # Verificar que la partida esté en fase nocturna
    if game.status != GameStatus.NIGHT:
        return None
    
    # Verificar que el atacante existe y está vivo
    if attacker_id not in game.roles:
        return None
    
    attacker_role = game.roles[attacker_id]
    if not attacker_role.is_alive:
        return None
    
    # Verificar que el atacante es un hombre lobo
    if attacker_role.role != GameRole.WAREWOLF:
        return None
    
    # Verificar que el objetivo existe y está vivo
    if target_id not in game.roles:
        return None
    
    target_role = game.roles[target_id]
    if not target_role.is_alive:
        return None
    
    # Verificar que el objetivo no es un hombre lobo (no pueden atacarse entre ellos)
    if target_role.role == GameRole.WAREWOLF:
        return None
    
    # Verificar que el hombre lobo no ha actuado ya esta noche
    if attacker_role.has_acted_tonight:
        return None
    
    # Registrar la acción del hombre lobo
    game.roles[attacker_id].has_acted_tonight = True
    game.roles[attacker_id].target_player_id = target_id
    
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
        player_id for player_id, role_info in game.roles.items()
        if role_info.role == GameRole.WAREWOLF and role_info.is_alive
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


def get_alive_players(game_id: str) -> List[Dict[str, str]]:
    """
    Obtiene la lista de jugadores vivos de la partida.
    
    Args:
        game_id: ID de la partida
    
    Returns:
        Lista de diccionarios con id y nombre de jugadores vivos
    """
    from app.database import load_game, load_user
    game = load_game(game_id)
    if not game:
        return []
    
    alive_players = []
    for player_id in game.players:
        if player_id in game.roles and game.roles[player_id].is_alive:
            user = load_user(player_id)
            if user:
                alive_players.append({
                    "id": user.id,
                    "username": user.username
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
    from app.database import load_game, load_user
    game = load_game(game_id)
    if not game:
        return []
    
    valid_targets = []
    for player_id in game.players:
        if (player_id in game.roles and 
            game.roles[player_id].is_alive and 
            game.roles[player_id].role != GameRole.WAREWOLF):
            user = load_user(player_id)
            if user:
                valid_targets.append({
                    "id": user.id,
                    "username": user.username
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
    if player_id not in game.roles:
        return False
    
    player_role = game.roles[player_id]
    if not player_role.is_alive:
        return False
    
    # Verificar que es un hombre lobo
    if player_role.role != GameRole.WAREWOLF:
        return False
    
    # Verificar que no ha actuado esta noche
    if player_role.has_acted_tonight:
        return False
    
    return True



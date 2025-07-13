"""
Módulo de servicios para las acciones de los jugadores durante las partidas.
Incluye funciones para que los jugadores realicen sus acciones nocturnas específicas según su rol.
"""

from app.database import save_game, load_game
from app.models.game import Game, GameStatus
from app.models.roles import GameRole
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
        if player.id in game.roles and game.roles[player.id].is_alive:
            alive_players.append({
                "id": player.id,
                "username": player.username
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
        if (player.id in game.roles and 
            game.roles[player.id].is_alive and 
            game.roles[player.id].role != GameRole.WAREWOLF):
            valid_targets.append({
                "id": player.id,
                "username": player.username
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
    if voter_id not in game.roles:
        return None
    
    voter_role = game.roles[voter_id]
    if not voter_role.is_alive:
        return None
    
    # Verificar que el objetivo existe y está vivo
    if target_id not in game.roles:
        return None
    
    target_role = game.roles[target_id]
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
        if player.id in game.roles and game.roles[player.id].is_alive:
            count = vote_counts.get(player.id, 0)
            vote_results.append({
                "player_id": player.id,
                "username": player.username,
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
    if player_id not in game.roles:
        return False
    
    player_role = game.roles[player_id]
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
        if player.id in game.roles and game.roles[player.id].is_alive:
            eligible_players.append({
                "id": player.id,
                "username": player.username
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
    alive_players = [p for p in game.players if p.id in game.roles and game.roles[p.id].is_alive]
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

def can_seer_act(game_id: str, player_id: str) -> bool:
    """
    Verifica si un jugador puede usar la habilidad de vidente.
    
    Args:
        game_id: ID de la partida
        player_id: ID del jugador
    
    Returns:
        True si puede actuar como vidente, False en caso contrario
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
    
    # Verificar que el jugador es una vidente
    if player_role.role != GameRole.SEER:
        return False
    
    # Verificar que no ha usado su habilidad esta noche
    if player_role.has_used_vision_tonight:
        return False
    
    return True


def seer_vision(game_id: str, seer_id: str, target_id: str) -> Optional[Game]:
    """
    Permite a la vidente investigar el rol de otro jugador.
    
    Args:
        game_id: ID de la partida
        seer_id: ID del jugador vidente
        target_id: ID del jugador a investigar
    
    Returns:
        Game actualizado si la acción fue exitosa, None en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return None
    
    # Verificar que la vidente puede actuar
    if not can_seer_act(game_id, seer_id):
        return None
    
    # Verificar que el objetivo existe y está vivo
    if target_id not in game.roles:
        return None
    
    target_role = game.roles[target_id]
    if not target_role.is_alive:
        return None
    
    # No puede investigarse a sí misma
    if seer_id == target_id:
        return None
    
    # Marcar que la vidente ya usó su habilidad esta noche
    seer_role = game.roles[seer_id]
    seer_role.has_used_vision_tonight = True
    seer_role.target_player_id = target_id
    
    # Guardar la partida
    save_game(game)
    return game


def get_seer_vision_result(game_id: str, seer_id: str, target_id: str) -> Optional[Dict[str, str]]:
    """
    Obtiene el resultado de la visión de la vidente sobre un jugador objetivo.
    
    Args:
        game_id: ID de la partida
        seer_id: ID del jugador vidente
        target_id: ID del jugador investigado
    
    Returns:
        Diccionario con el rol y username del objetivo, None si no es válido
    """
    game = load_game(game_id)
    if not game:
        return None
    
    # Verificar que el vidente existe y es vidente
    if seer_id not in game.roles:
        return None
    
    seer_role = game.roles[seer_id]
    if seer_role.role != GameRole.SEER:
        return None
    
    # Verificar que el objetivo existe
    if target_id not in game.roles:
        return None
    
    target_role = game.roles[target_id]
    
    # Buscar el username del objetivo
    target_username = None
    for player in game.players:
        if player.id == target_id:
            target_username = player.username
            break
    
    if not target_username:
        return None
    
    return {
        "role": target_role.role.value,
        "username": target_username
    }


def get_seer_eligible_targets(game_id: str, seer_id: str) -> List[Dict[str, str]]:
    """
    Obtiene la lista de jugadores que la vidente puede investigar.
    
    Args:
        game_id: ID de la partida
        seer_id: ID del jugador vidente
    
    Returns:
        Lista de jugadores vivos (excluyendo a la vidente)
    """
    game = load_game(game_id)
    if not game:
        return []
    
    eligible_targets = []
    
    for player in game.players:
        # Excluir a la propia vidente
        if player.id == seer_id:
            continue
        
        # Solo incluir jugadores vivos
        if player.id in game.roles:
            role_info = game.roles[player.id]
            if role_info.is_alive:
                eligible_targets.append({
                    "id": player.id,
                    "username": player.username
                })
    
    return eligible_targets


def reset_seer_night_actions(game_id: str) -> bool:
    """
    Reinicia las acciones nocturnas de la vidente para una nueva noche.
    
    Args:
        game_id: ID de la partida
    
    Returns:
        True si se reiniciaron correctamente, False en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return False
    
    # Reiniciar estado de la vidente
    for player_id, role_info in game.roles.items():
        if role_info.role == GameRole.SEER and role_info.is_alive:
            role_info.has_used_vision_tonight = False
            role_info.target_player_id = None
    
    save_game(game)
    return True


# Funciones para el Alguacil

def is_sheriff(game_id: str, player_id: str) -> bool:
    """
    Verifica si un jugador es el alguacil.
    
    Args:
        game_id: ID de la partida
        player_id: ID del jugador
    
    Returns:
        True si es el alguacil, False en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return False
    
    if player_id not in game.roles:
        return False
    
    player_role = game.roles[player_id]
    return player_role.role == GameRole.SHERIFF and player_role.is_alive


def can_sheriff_break_tie(game_id: str, sheriff_id: str) -> bool:
    """
    Verifica si el alguacil puede desempatar una votación.
    
    Args:
        game_id: ID de la partida
        sheriff_id: ID del alguacil
    
    Returns:
        True si puede desempatar, False en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return False
    
    # Verificar que es alguacil
    if not is_sheriff(game_id, sheriff_id):
        return False
    
    # Verificar que la partida esté en fase de día (cuando se votan linchamientos)
    if game.status != GameStatus.DAY:
        return False
    
    # Verificar si hay empate en la votación diurna
    return has_day_vote_tie(game_id)


def has_day_vote_tie(game_id: str) -> bool:
    """
    Verifica si hay empate en la votación diurna actual.
    
    Args:
        game_id: ID de la partida
    
    Returns:
        True si hay empate, False en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return False
    
    # Contar votos por jugador
    vote_counts = {}
    for voter_id, target_id in game.day_votes.items():
        if target_id in vote_counts:
            vote_counts[target_id] += 1
        else:
            vote_counts[target_id] = 1
    
    if not vote_counts:
        return False
    
    # Verificar si hay empate (al menos dos jugadores con el máximo de votos)
    max_votes = max(vote_counts.values())
    tied_players = [player_id for player_id, votes in vote_counts.items() if votes == max_votes]
    
    return len(tied_players) > 1


def sheriff_break_tie(game_id: str, sheriff_id: str, chosen_target_id: str) -> Optional[Game]:
    """
    Permite al alguacil desempatar una votación eligiendo quién será eliminado.
    
    Args:
        game_id: ID de la partida
        sheriff_id: ID del alguacil
        chosen_target_id: ID del jugador elegido para ser eliminado
    
    Returns:
        Game actualizado si la acción fue exitosa, None en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return None
    
    # Verificar que puede desempatar
    if not can_sheriff_break_tie(game_id, sheriff_id):
        return None
    
    # Verificar que el objetivo elegido está entre los empatados
    tied_players = get_tied_players(game_id)
    if chosen_target_id not in tied_players:
        return None
    
    # Verificar que el objetivo existe y está vivo
    if chosen_target_id not in game.roles:
        return None
    
    target_role = game.roles[chosen_target_id]
    if not target_role.is_alive:
        return None
    
    # Marcar al jugador como eliminado
    target_role.is_alive = False
    
    # Limpiar votos diurnos
    game.day_votes.clear()
    
    # Guardar la partida
    save_game(game)
    return game


def get_tied_players(game_id: str) -> List[str]:
    """
    Obtiene la lista de jugadores empatados en la votación diurna.
    
    Args:
        game_id: ID de la partida
    
    Returns:
        Lista de IDs de jugadores empatados
    """
    game = load_game(game_id)
    if not game:
        return []
    
    # Contar votos por jugador
    vote_counts = {}
    for voter_id, target_id in game.day_votes.items():
        if target_id in vote_counts:
            vote_counts[target_id] += 1
        else:
            vote_counts[target_id] = 1
    
    if not vote_counts:
        return []
    
    # Encontrar jugadores con el máximo de votos
    max_votes = max(vote_counts.values())
    tied_players = [player_id for player_id, votes in vote_counts.items() if votes == max_votes]
    
    return tied_players if len(tied_players) > 1 else []


def can_sheriff_choose_successor(game_id: str, sheriff_id: str) -> bool:
    """
    Verifica si el alguacil puede elegir un sucesor (cuando está a punto de morir).
    
    Args:
        game_id: ID de la partida
        sheriff_id: ID del alguacil
    
    Returns:
        True si puede elegir sucesor, False en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return False
    
    # Verificar que es alguacil
    if sheriff_id not in game.roles:
        return False
    
    sheriff_role = game.roles[sheriff_id]
    if sheriff_role.role != GameRole.SHERIFF:
        return False
    
    # El alguacil puede elegir sucesor si está vivo pero será eliminado
    # (en la práctica, esto se llamará cuando esté a punto de morir)
    return sheriff_role.is_alive


def sheriff_choose_successor(game_id: str, sheriff_id: str, successor_id: str) -> Optional[Game]:
    """
    Permite al alguacil elegir a su sucesor antes de morir.
    
    Args:
        game_id: ID de la partida
        sheriff_id: ID del alguacil
        successor_id: ID del jugador elegido como sucesor
    
    Returns:
        Game actualizado si la acción fue exitosa, None en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return None
    
    # Verificar que puede elegir sucesor
    if not can_sheriff_choose_successor(game_id, sheriff_id):
        return None
    
    # Verificar que el sucesor existe y está vivo
    if successor_id not in game.roles:
        return None
    
    successor_role = game.roles[successor_id]
    if not successor_role.is_alive:
        return None
    
    # No puede elegirse a sí mismo como sucesor
    if sheriff_id == successor_id:
        return None
    
    # Registrar al sucesor en el rol del alguacil actual
    sheriff_role = game.roles[sheriff_id]
    sheriff_role.successor_id = successor_id
    
    # El sucesor se convertirá en alguacil cuando el actual muera
    # (esto se procesará en otra función cuando efectivamente muera)
    
    save_game(game)
    return game


def promote_sheriff_successor(game_id: str, deceased_sheriff_id: str) -> Optional[Game]:
    """
    Promueve al sucesor del alguacil cuando el alguacil actual muere.
    
    Args:
        game_id: ID de la partida
        deceased_sheriff_id: ID del alguacil que ha muerto
    
    Returns:
        Game actualizado si la promoción fue exitosa, None en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return None
    
    # Verificar que el alguacil muerto tenía un sucesor designado
    if deceased_sheriff_id not in game.roles:
        return None
    
    deceased_sheriff_role = game.roles[deceased_sheriff_id]
    if deceased_sheriff_role.role != GameRole.SHERIFF or not deceased_sheriff_role.successor_id:
        return None
    
    successor_id = deceased_sheriff_role.successor_id
    
    # Verificar que el sucesor existe y está vivo
    if successor_id not in game.roles:
        return None
    
    successor_role = game.roles[successor_id]
    if not successor_role.is_alive:
        return None
    
    # Promover al sucesor a alguacil
    successor_role.role = GameRole.SHERIFF
    successor_role.has_double_vote = True
    successor_role.can_break_ties = True
    
    save_game(game)
    return game


def get_sheriff_eligible_successors(game_id: str, sheriff_id: str) -> List[Dict[str, str]]:
    """
    Obtiene la lista de jugadores que pueden ser elegidos como sucesores del alguacil.
    
    Args:
        game_id: ID de la partida
        sheriff_id: ID del alguacil
    
    Returns:
        Lista de jugadores vivos (excluyendo al alguacil)
    """
    game = load_game(game_id)
    if not game:
        return []
    
    eligible_successors = []
    
    for player in game.players:
        # Excluir al propio alguacil
        if player.id == sheriff_id:
            continue
        
        # Solo incluir jugadores vivos
        if player.id in game.roles:
            role_info = game.roles[player.id]
            if role_info.is_alive:
                eligible_successors.append({
                    "id": player.id,
                    "username": player.username
                })
    
    return eligible_successors


def get_tied_players_info(game_id: str) -> List[Dict[str, str]]:
    """
    Obtiene información de los jugadores empatados en la votación diurna.
    
    Args:
        game_id: ID de la partida
    
    Returns:
        Lista de jugadores empatados con su información
    """
    game = load_game(game_id)
    if not game:
        return []
    
    tied_player_ids = get_tied_players(game_id)
    tied_players_info = []
    
    for player in game.players:
        if player.id in tied_player_ids:
            tied_players_info.append({
                "id": player.id,
                "username": player.username
            })
    
    return tied_players_info



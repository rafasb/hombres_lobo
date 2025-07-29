"""
Módulo de servicios para las acciones de los jugadores durante las partidas.
Incluye funciones para que los jugadores realicen sus acciones nocturnas específicas según su rol.
"""

from app.database import save_game, load_game
from app.models.game_and_roles import Game, GameStatus, GameRole
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
    
    if player_id not in game.roles:
        return False
    
    player_role = game.roles[player_id]
    return player_role.role == GameRole.HUNTER


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
    if hunter_id not in game.roles:
        return False
    
    hunter_role = game.roles[hunter_id]
    if hunter_role.role != GameRole.HUNTER:
        return False
    
    # El cazador puede vengarse si está muerto pero no ha usado su venganza
    if hunter_role.is_alive:
        return False
    
    # Verificar que no ha usado ya su habilidad de venganza
    if hunter_role.has_used_revenge:
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
    if target_id not in game.roles:
        return None
    
    target_role = game.roles[target_id]
    if not target_role.is_alive:
        return None
    
    # No puede vengarse de sí mismo (aunque ya esté muerto)
    if hunter_id == target_id:
        return None
    
    # Marcar al objetivo como muerto
    target_role.is_alive = False
    
    # Marcar que el cazador ya usó su venganza
    hunter_role = game.roles[hunter_id]
    hunter_role.has_used_revenge = True
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
    if hunter_id not in game.roles:
        return None
    
    hunter_role = game.roles[hunter_id]
    if hunter_role.role != GameRole.HUNTER or not hunter_role.is_alive:
        return None
    
    # Marcar como muerto pero con venganza disponible
    hunter_role.is_alive = False
    hunter_role.can_revenge_kill = True
    hunter_role.has_used_revenge = False
    
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
        if player.id == hunter_id:
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
    
    for player_id, role_info in game.roles.items():
        if (role_info.role == GameRole.HUNTER and 
            not role_info.is_alive and 
            not role_info.has_used_revenge and
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
    
    if hunter_id not in game.roles:
        return None
    
    hunter_role = game.roles[hunter_id]
    if (hunter_role.role != GameRole.HUNTER or 
        not hunter_role.has_used_revenge or 
        not hunter_role.target_player_id):
        return None
    
    # Buscar información del objetivo
    target_id = hunter_role.target_player_id
    for player in game.players:
        if player.id == target_id:
            return {
                "id": target_id,
                "username": player.username
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
    
    if hunter_id not in game.roles:
        return False
    
    hunter_role = game.roles[hunter_id]
    if hunter_role.role != GameRole.HUNTER:
        return False
    
    # Reiniciar estado de venganza
    hunter_role.can_revenge_kill = False
    hunter_role.has_used_revenge = False
    hunter_role.target_player_id = None
    
    save_game(game)
    return True


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
    
    if player_id not in game.roles:
        return False
    
    player_role = game.roles[player_id]
    return player_role.role == GameRole.WITCH and player_role.is_alive


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
    
    witch_role = game.roles[witch_id]
    
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
    
    witch_role = game.roles[witch_id]
    
    # Verificar que aún tiene la poción de veneno
    if not witch_role.has_poison_potion:
        return False
    
    return True


def get_warewolf_attack_victim(game_id: str) -> Optional[str]:
    """
    Obtiene el ID del jugador atacado por los hombres lobo esta noche.
    
    Args:
        game_id: ID de la partida
    
    Returns:
        ID del jugador atacado, None si no hay ataque o consenso
    """
    return get_warewolf_attack_consensus(game_id)


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
    if victim_id not in game.roles:
        return None
    
    # Marcar que la bruja usó su poción de curación
    witch_role = game.roles[witch_id]
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
    if target_id not in game.roles:
        return None
    
    target_role = game.roles[target_id]
    if not target_role.is_alive:
        return None
    
    # La bruja puede envenenarse a sí misma si quiere
    # (no hay restricción en las reglas tradicionales)
    
    # Marcar que la bruja usó su poción de veneno
    witch_role = game.roles[witch_id]
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
    
    witch_role = game.roles[witch_id]
    
    # Obtener información del ataque de lobos
    attack_victim_id = get_warewolf_attack_victim(game_id)
    attack_victim_username = None
    
    if attack_victim_id:
        for player in game.players:
            if player.id == attack_victim_id:
                attack_victim_username = player.username
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
        if player.id in game.roles:
            role_info = game.roles[player.id]
            if role_info.is_alive:
                eligible_targets.append({
                    "id": player.id,
                    "username": player.username
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
            if target_id in game.roles:
                game.roles[target_id].is_alive = False
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
    
    if witch_id not in game.roles:
        return False
    
    witch_role = game.roles[witch_id]
    if witch_role.role != GameRole.WITCH:
        return False
    
    # Inicializar pociones
    witch_role.has_healing_potion = True
    witch_role.has_poison_potion = True
    
    save_game(game)
    return True


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
    
    if player_id not in game.roles:
        return False
    
    player_role = game.roles[player_id]
    return player_role.role == GameRole.WILD_CHILD and player_role.is_alive


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
    
    wild_child_role = game.roles[wild_child_id]
    
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
        if player.id != wild_child_id and player.id in game.roles:
            role_info = game.roles[player.id]
            if role_info.is_alive:
                available_models.append({
                    "id": player.id,
                    "username": player.username
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
    if model_player_id not in game.roles:
        return None
    
    model_role = game.roles[model_player_id]
    if not model_role.is_alive:
        return None
    
    # El modelo no puede ser él mismo
    if model_player_id == wild_child_id:
        return None
    
    # Asignar el modelo
    wild_child_role = game.roles[wild_child_id]
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
    
    if wild_child_id not in game.roles:
        return {}
    
    wild_child_role = game.roles[wild_child_id]
    
    # Verificar que era originalmente Niño Salvaje (puede haber cambiado a WAREWOLF)
    if wild_child_role.role not in [GameRole.WILD_CHILD, GameRole.WAREWOLF]:
        return {}
    
    model_username = None
    if wild_child_role.model_player_id:
        for player in game.players:
            if player.id == wild_child_role.model_player_id:
                model_username = player.username
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
    for player_id, role_info in game.roles.items():
        if (role_info.role == GameRole.WILD_CHILD and 
            role_info.is_alive and 
            role_info.model_player_id == dead_player_id and
            not role_info.has_transformed):
            
            # Transformar al Niño Salvaje en Hombre Lobo
            role_info.has_transformed = True
            role_info.role = GameRole.WAREWOLF
            
            # Obtener nombre del jugador
            player_username = None
            for player in game.players:
                if player.id == player_id:
                    player_username = player.username
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
    
    for player_id, role_info in game.roles.items():
        if (role_info.role == GameRole.WAREWOLF and 
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
    
    if wild_child_id not in game.roles:
        return {}
    
    wild_child_role = game.roles[wild_child_id]
    
    # Si no era Niño Salvaje originalmente, no aplica
    if wild_child_role.role not in [GameRole.WILD_CHILD, GameRole.WAREWOLF]:
        return {}
    
    model_username = None
    model_is_alive = False
    
    if wild_child_role.model_player_id:
        for player in game.players:
            if player.id == wild_child_role.model_player_id:
                model_username = player.username
                if wild_child_role.model_player_id in game.roles:
                    model_is_alive = game.roles[wild_child_role.model_player_id].is_alive
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
    
    if wild_child_id not in game.roles:
        return False
    
    wild_child_role = game.roles[wild_child_id]
    if wild_child_role.role != GameRole.WILD_CHILD:
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
    for player_id, role_info in game.roles.items():
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
    
    if player_id not in game.roles:
        return False
    
    game.roles[player_id].is_alive = False
    save_game(game)
    return True


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
    
    if player_id not in game.roles:
        return False
    
    return game.roles[player_id].role == GameRole.CUPID


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
    if not game.roles[cupid_id].is_alive:
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
        if (player.id in game.roles and 
            game.roles[player.id].is_alive):
            available_targets.append({
                "id": player.id,
                "username": player.username
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
    if lover1_id not in game.roles or lover2_id not in game.roles:
        return None
    
    if not game.roles[lover1_id].is_alive or not game.roles[lover2_id].is_alive:
        return None
    
    # Los enamorados deben ser diferentes
    if lover1_id == lover2_id:
        return None
    
    # Marcar a los jugadores como enamorados
    game.roles[lover1_id].is_lover = True
    game.roles[lover1_id].lover_partner_id = lover2_id
    
    game.roles[lover2_id].is_lover = True
    game.roles[lover2_id].lover_partner_id = lover1_id
    
    # Marcar a Cupido como que ya eligió
    game.roles[cupid_id].is_cupid = True
    
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
                if player.id == lover1_id:
                    lover1_username = player.username
                elif player.id == lover2_id:
                    lover2_username = player.username
    
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
    
    if player_id not in game.roles:
        return {
            "is_lover": False,
            "partner_id": None,
            "partner_username": None,
            "both_alive": False
        }
    
    role_info = game.roles[player_id]
    
    if not role_info.is_lover:
        return {
            "is_lover": False,
            "partner_id": None,
            "partner_username": None,
            "both_alive": False
        }
    
    partner_id = role_info.lover_partner_id
    partner_username = None
    both_alive = False
    
    if partner_id and partner_id in game.roles:
        # Obtener nombre del compañero
        for player in game.players:
            if player.id == partner_id:
                partner_username = player.username
                break
        
        # Verificar si ambos están vivos
        both_alive = role_info.is_alive and game.roles[partner_id].is_alive
    
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
    if (dead_player_id in game.roles and 
        game.roles[dead_player_id].is_lover and 
        game.roles[dead_player_id].lover_partner_id):
        
        partner_id = game.roles[dead_player_id].lover_partner_id
        
        # Si el compañero aún está vivo, muere de pena
        if (partner_id in game.roles and 
            game.roles[partner_id].is_alive):
            
            game.roles[partner_id].is_alive = False
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
    for player_id, role_info in game.roles.items():
        if role_info.is_alive:
            alive_players.append(player_id)
    
    # Si solo quedan 2 jugadores vivos, verificar si son enamorados
    if len(alive_players) == 2:
        player1_id = alive_players[0]
        player2_id = alive_players[1]
        
        # Verificar si ambos son enamorados y están enlazados entre sí
        if (game.roles[player1_id].is_lover and 
            game.roles[player2_id].is_lover and
            game.roles[player1_id].lover_partner_id == player2_id and
            game.roles[player2_id].lover_partner_id == player1_id):
            
            # Obtener nombres de usuario
            player1_username = None
            player2_username = None
            for player in game.players:
                if player.id == player1_id:
                    player1_username = player.username
                elif player.id == player2_id:
                    player2_username = player.username
            
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
    game.roles[cupid_id].is_cupid = True
    
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



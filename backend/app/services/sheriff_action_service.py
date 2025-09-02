
from app.database import load_game, save_game
from app.models.game_and_player import GameStatus, Roles
from app.models.game_and_player import Game, PlayerInfo
from typing import Optional, List, Dict
from app.services.user_service import UserService

# Funciones para el Alguacil

class SheriffService(PlayerInfo):
    def __init__(self, **data):
        super().__init__(**data)
    def reset_night_action(self):
        self.has_acted_tonight = False
        self.target_player_id = None
    def mark_acted(self):
        self.has_acted_tonight = True
    def set_target(self, target_id: str):
        self.target_player_id = target_id
    def can_act(self) -> bool:
        '''Verifica si el alguacil puede actuar esta noche.
        Si está muerto o ya ha actuado, no puede.'''
        return not self.has_acted_tonight and self.is_alive
    def has_acted(self) -> bool:
        if self.has_acted_tonight is None:
            self.has_acted_tonight = False
            return self.has_acted_tonight
        else:
            return self.has_acted_tonight

def get_sheriff_id(game: Game) -> Optional[str]:
    '''Busca y retorna el ID del jugador alguacil en la partida, o None si no hay alguacil.'''
    for player_id, role_info in game.players.items():
        if role_info.role == Roles.SHERIFF and role_info.is_alive:
            return player_id
    return None

def get_sheriff_service(game: Game | str, sheriff_id: str) -> Optional[SheriffService]:
    if isinstance(game, str):
        game_obj = load_game(game)
    else:
        game_obj = game
    if game_obj is None:
        return None
    try:
        player_state = game_obj.get_player_state(sheriff_id)
        if player_state is None:
            print(f"Error: player_id {sheriff_id} not found in game {game_obj.id}.")
            return None
        elif isinstance(player_state, PlayerInfo):
            sheriff_data = player_state.model_dump()
            if sheriff_data.get("role") != Roles.SHERIFF:
                print(f"Error: player_id {sheriff_id} in game {game_obj.id} is not a Sheriff.")
                return None
            sheriff_role = SheriffService(**sheriff_data)
        else:
            print(f"Error: player_id {sheriff_id} in game {game_obj.id} has invalid state type.")
            return None
    except Exception:
        print(f"Error: player_id {sheriff_id} in game {game_obj.id} has invalid role data.")
        return None
    return sheriff_role

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
    
    if player_id not in game.players:
        return False
    
    player_role = game.players[player_id]
    return player_role.role == Roles.SHERIFF and player_role.is_alive

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
    if chosen_target_id not in game.players:
        return None
    
    target_role = game.players[chosen_target_id]
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
    if sheriff_id not in game.players:
        return False
    
    sheriff_role = game.players[sheriff_id]
    if sheriff_role.role != Roles.SHERIFF:
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
    if successor_id not in game.players:
        return None
    
    successor_role = game.players[successor_id]
    if not successor_role.is_alive:
        return None
    
    # No puede elegirse a sí mismo como sucesor
    if sheriff_id == successor_id:
        return None
    
    # Registrar al sucesor en el rol del alguacil actual
    sheriff_role = game.players[sheriff_id]
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
    if deceased_sheriff_id not in game.players:
        return None
    
    deceased_sheriff_role = game.players[deceased_sheriff_id]
    if deceased_sheriff_role.role != Roles.SHERIFF or not deceased_sheriff_role.successor_id:
        return None
    
    successor_id = deceased_sheriff_role.successor_id
    
    # Verificar que el sucesor existe y está vivo
    if successor_id not in game.players:
        return None
    
    successor_role = game.players[successor_id]
    if not successor_role.is_alive:
        return None
    
    # Promover al sucesor a alguacil
    successor_role.role = Roles.SHERIFF
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
        if player == sheriff_id:
            continue
        
        # Solo incluir jugadores vivos
        if player in game.players:
            role_info = game.players[player]
            if role_info.is_alive:
                eligible_successors.append({
                    "id": player,
                    "username": UserService.get_username_by_id(player)
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
        if player in tied_player_ids:
            tied_players_info.append({
                "id": player,
                "username": UserService.get_username_by_id(player)
            })
    
    return tied_players_info

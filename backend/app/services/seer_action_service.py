from app.database import save_game, load_game
from app.models.game_and_player import Game, Roles, PlayerInfo
from app.services.user_service import UserService
from typing import Optional, List, Dict, Any
from app.services.player_action_service import get_alive_players, is_valid_target
from enum import Enum

# Funciones para la Vidente

class SeerService(PlayerInfo):
    def __init__(self, **data):
        super().__init__(**data)
    def reset_night_action(self):
        self.has_acted_tonight = False
        self.has_used_vision_tonight = False
        self.target_player_id = None
    def mark_acted(self):
        self.has_acted_tonight = True
        self.has_used_vision_tonight = True
    def set_target(self, target_id: str):
        self.target_player_id = target_id
    def can_act(self) -> bool:
        '''Verifica si la vidente puede actuar esta noche.
        Si está muerta o ya ha actuado, no puede.'''
        return not self.has_acted_tonight and self.is_alive
    def has_acted(self) -> bool:
        if self.has_acted_tonight is None:
            self.has_acted_tonight = False
            return self.has_acted_tonight
        else:
            return self.has_acted_tonight

# Helper: normalizar una entrada player (puede ser PlayerInfo, dict o BaseModel) a PlayerInfo
def _normalize_player_entry(entry: Any) -> Optional[PlayerInfo]:
    if entry is None:
        return None
    if isinstance(entry, PlayerInfo):
        return entry
    # pydantic v2 models expose model_dump
    if hasattr(entry, "model_dump"):
        try:
            return PlayerInfo(**entry.model_dump())
        except Exception:
            return None
    if isinstance(entry, dict):
        try:
            return PlayerInfo(**entry)
        except Exception:
            return None
    return None

def get_seer_id(game: Game) -> Optional[str]:
    '''Busca y retorna el ID del jugador vidente en la partida, o None si no hay vidente.'''
    for player_id, role_info in game.players.items():
        normalized = _normalize_player_entry(role_info)
        if not normalized:
            continue
        if normalized.role == Roles.SEER and normalized.is_alive:
            return player_id
    return None

def is_seer(game_id: str, player_id: str) -> bool:
    """
    Verifica si un jugador es la vidente en una partida.
    
    Args:
        game_id: ID de la partida
        player_id: ID del jugador
    
    Returns:
        True si el jugador es la vidente, False en caso contrario
    """
    game = load_game(game_id)
    if not game:
        return False
    player_role = game.players.get(player_id)
    if not player_role:
        return False
    normalized = _normalize_player_entry(player_role)
    if not normalized:
        return False
    return normalized.role == Roles.SEER

def get_seer_service(game: Game | str, seer_id: str) -> Optional[PlayerInfo]:
    if isinstance(game, str):
        game_obj = load_game(game)
    else:
        game_obj = game
    if game_obj is None:
        return None
    seer_data = game_obj.players.get(seer_id)
    if not seer_data:
        return None
    try:
        data_dict = seer_data.model_dump() if hasattr(seer_data, "model_dump") else dict(seer_data)
        seer_role = PlayerInfo(**data_dict)
    except Exception as e:
        print(f"Error: player_id {seer_id} in game {getattr(game_obj, 'id', '<unknown>')} has invalid role data: {e}")
        return None
    return seer_role


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

    # Obtener y normalizar el objeto del jugador en la partida
    raw_seer = game.players.get(seer_id)
    if not raw_seer:
        return None
    seer_obj = _normalize_player_entry(raw_seer)
    if not seer_obj or seer_obj.role != Roles.SEER:
        return None

    # Usar wrapper para evaluar reglas (can_act) sin modificar el original hasta confirmar
    try:
        seer_wrapper = PlayerInfo(**(seer_obj.model_dump() if hasattr(seer_obj, "model_dump") else {}))
    except Exception:
        return None

    if not getattr(seer_wrapper, "can_act", lambda: not seer_wrapper.has_acted_tonight and seer_wrapper.is_alive)():
        # Si PlayerInfo no define can_act, asumimos los campos
        # (Nota: PlayerInfo en models puede no tener métodos; aquí comprobamos estado simple)
        if seer_wrapper.has_acted_tonight or not seer_wrapper.is_alive:
            return None

    # Verificar que el objetivo existe y está vivo
    if is_valid_target(game, target_id) is False:
        return None

    # No puede investigarse a sí misma
    if seer_id == target_id:
        return None

    # Crear una instancia PlayerInfo actualizable, aplicar cambios y reasignar para persistir
    updated_seer = _normalize_player_entry(raw_seer)
    if not updated_seer:
        return None
    updated_seer.target_player_id = target_id
    updated_seer.has_acted_tonight = True

    # Reasignar en el mapa de players para que save_game persista el cambio
    game.players[seer_id] = updated_seer

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
    
    seer_role = get_seer_service(game, seer_id)
    if not seer_role:
        return None
    
    # Verificar que el objetivo existe y está vivo
    if is_valid_target(game, target_id) is False:
        return None
    
    target_raw = game.players.get(target_id)
    if not target_raw:
        return None
    target_normalized = _normalize_player_entry(target_raw)
    if not target_normalized:
        return None

    # Buscar el username del objetivo
    target_username = UserService.get_username_by_id(target_id)
    if not target_username:
        return None

    return {
        "role": target_normalized.role.value if isinstance(target_normalized.role, Enum) else str(target_normalized.role),
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
    
    eligible_targets = get_alive_players(game_id, exclude=seer_id)
    
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

    seer_id = get_seer_id(game)
    if not seer_id:
        return False

    raw_seer = game.players.get(seer_id)
    if not raw_seer:
        return False

    updated_seer = _normalize_player_entry(raw_seer)
    if not updated_seer:
        return False

    updated_seer.has_acted_tonight = False

    updated_seer.target_player_id = None

    game.players[seer_id] = updated_seer
    save_game(game)
    return True
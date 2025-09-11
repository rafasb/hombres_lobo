"""
Ejemplos de uso para las clases GameResponse y PublicPlayerInfo.
Este archivo muestra cómo construir y usar las nuevas clases de respuesta.
"""

from datetime import datetime, UTC
from app.models.game_responses import GameResponse, PublicPlayerInfo, GameStateUpdateResponse
from app.models.game_and_player import GameStatus
from app.models.user import UserStatus


def example_public_player_info():
    """Ejemplo de cómo crear información pública de un jugador."""
    player_info = PublicPlayerInfo(
        player_id="player_123",
        username="LoboBueno",
        is_alive=True,
        # is_connected=True,
        user_status=UserStatus.IN_GAME
    )
    return player_info


def example_game_response():
    """Ejemplo de cómo crear una respuesta completa del juego."""
    players = [
        PublicPlayerInfo(
            player_id="player_123",
            username="LoboBueno",
            is_alive=True,
            # is_connected=True,
            user_status=UserStatus.IN_GAME
        ),
        PublicPlayerInfo(
            player_id="player_456",
            username="AldeanaAstuta",
            is_alive=True,
            # is_connected=False,
            user_status=UserStatus.DISCONNECTED
        ),
        PublicPlayerInfo(
            player_id="player_789",
            username="VidenteSabio",
            is_alive=False,
            # is_connected=True,
            user_status=UserStatus.IN_GAME
        )
    ]
    
    game_response = GameResponse(
        game_id="game_abc123",
        name="Partida de Medianoche",
        creator_id="player_123",
        creator_name="LoboBueno",
        status=GameStatus.NIGHT,
        current_round=3,
        is_first_night=False,
        max_players=8,
        current_players=3,
        players=players,
        eliminated_players=["player_789"],
        connected_players_count=2,
        created_at=datetime.now(UTC),
        success=True,
        message="Estado del juego actualizado"
    )
    return game_response


def example_game_state_update():
    """Ejemplo de cómo crear una actualización de estado simplificada."""
    players = [
        PublicPlayerInfo(
            player_id="player_123",
            username="LoboBueno",
            is_alive=True,
            # is_connected=True,
            user_status=UserStatus.IN_GAME
        ),
        PublicPlayerInfo(
            player_id="player_456",
            username="AldeanaAstuta",
            is_alive=True,
            # is_connected=True,
            user_status=UserStatus.IN_GAME
        )
    ]
    
    update_response = GameStateUpdateResponse(
        game_id="game_abc123",
        status=GameStatus.DAY,
        current_round=4,
        current_players=2,
        connected_players_count=2,
        players=players,
        eliminated_players=["player_789"],
        update_type="phase_change",
        timestamp=datetime.now(UTC)
    )
    return update_response


# Función auxiliar que podría usarse en un servicio futuro
def build_game_response_from_game_and_users(game, users_dict):
    """
    Función helper que muestra cómo construir un GameResponse 
    a partir de un objeto Game y un diccionario de usuarios.
    
    Args:
        game: Instancia del modelo Game
        users_dict: Diccionario {user_id: User} con información de usuarios
    
    Returns:
        GameResponse con toda la información pública
    """
    
    # Construir lista de jugadores públicos
    public_players = []
    for player_id in game.player_ids:
        if player_id in users_dict:
            user = users_dict[player_id]
            player_info = game.get_player_state(player_id)
            
            public_player = PublicPlayerInfo(
                player_id=player_id,
                username=user.username,
                is_alive=player_info.is_alive if player_info else True,
                # is_connected=player_id in game.connected_players,
                user_status=user.status
            )
            public_players.append(public_player)
    
    # Obtener nombre del creador
    creator_name = users_dict.get(game.creator_id, {}).username if game.creator_id in users_dict else "Desconocido"
    
    return GameResponse(
        game_id=game.id,
        name=game.name,
        creator_id=game.creator_id,
        creator_name=creator_name,
        status=game.status,
        current_round=game.current_round,
        is_first_night=game.is_first_night,
        max_players=game.max_players,
        current_players=len(game.player_ids),
        players=public_players,
        eliminated_players=game.eliminated_players,
        connected_players_count=len(game.connected_players),
        created_at=game.created_at
    )


if __name__ == "__main__":
    # Ejecutar ejemplos
    print("=== Ejemplo PublicPlayerInfo ===")
    player = example_public_player_info()
    print(player.model_dump_json(indent=2))
    
    print("\n=== Ejemplo GameResponse ===")
    game_resp = example_game_response()
    print(game_resp.model_dump_json(indent=2))
    
    print("\n=== Ejemplo GameStateUpdateResponse ===")
    state_update = example_game_state_update()
    print(state_update.model_dump_json(indent=2))

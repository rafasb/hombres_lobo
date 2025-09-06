"""
Rutas de API para la gestión de partidas.
Incluye endpoints para crear, consultar y listar partidas.
Requiere autenticación JWT para acceder.
"""

from fastapi import APIRouter, Depends
from app.models.game_and_player import Game, GameCreate, GameStatus
from app.models.game_responses import (
    GameGetResponse,
    GameListResponse,
)
from app.services.user_service import (
    UserService
)
from app.services.game_service import (
    create_game,
    get_all_games,
)
from app.core.dependencies import get_current_user
import uuid

router = APIRouter(prefix="/games", tags=["games"])


@router.post("", response_model=GameGetResponse)
def create_new_game(game: GameCreate, user=Depends(get_current_user)):
    new_game = Game(
        id=str(uuid.uuid4()),
        name=game.name,
        creator_id=game.creator_id,
        max_players=game.max_players,
        player_ids=[user.id],  # Solo almacenamos el ID del creador
        players={},
        status=GameStatus.WAITING
    )
    create_game(new_game)
    
    return GameGetResponse(
        success=True,
        message=f"Partida '{game.name}' creada exitosamente",
        game=new_game
    )


# Nueva versión del endpoint de listado de partidas
@router.get("", response_model=GameListResponse)
def list_games_v2(user=Depends(get_current_user)):
    games = get_all_games()
    
    # Construir la lista de resúmenes de partidas
    game_summaries = []
    for game in games:
        creator_name = UserService.get_username_by_id(game.creator_id) or "Desconocido"
        # Determinar el número actual de jugadores
        current_players_count = len(game.player_ids) if game.player_ids is not None else 0

        summary = GameListResponse.GameSummary(
            id=game.id,
            name=game.name,
            creator_name=creator_name,
            creator_id=game.creator_id,
            created_at=game.created_at.isoformat() if game.created_at else None,
            current_round=game.current_round,
            current_players=current_players_count,
            max_players=game.max_players,
            status=game.status.value,
            player_ids=game.player_ids  # Incluir player_ids si es necesario
        )
        game_summaries.append(summary)
    
    return GameListResponse(
        success=True,
        games=game_summaries,
        total_games=len(game_summaries)
    )


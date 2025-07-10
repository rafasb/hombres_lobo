"""
Rutas de API para la gestión de partidas.
Incluye endpoints para crear, consultar y listar partidas.
"""

from fastapi import APIRouter, HTTPException
from app.models.game import Game, GameCreate, GameStatus
from app.services.game_service import create_game, get_game, get_all_games
import uuid

router = APIRouter()

@router.post("/games", response_model=Game)
def create_new_game(game: GameCreate):
    new_game = Game(
        id=str(uuid.uuid4()),
        name=game.name,
        creator_id=game.creator_id,
        players=[],
        roles={},
        status=GameStatus.WAITING,
        max_players=game.max_players
    )
    create_game(new_game)
    return new_game

@router.get("/games/{game_id}", response_model=Game)
def get_game_by_id(game_id: str):
    game = get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Partida no encontrada")
    return game

@router.get("/games", response_model=list[Game])
def list_games():
    return get_all_games()

from app.database import save_user, load_user, load_all_users, save_game, load_game, load_all_games, delete_user, delete_game
from app.models.user import User, UserRole, UserStatus
from app.models.game import Game, GameStatus
import uuid

def test_save_and_load_user():
    user = User(
        id=str(uuid.uuid4()),
        username="testuser",
        email="test@example.com",
        role=UserRole.PLAYER,
        status=UserStatus.ACTIVE,
        hashed_password="hashedpass"
    )
    save_user(user)
    loaded = load_user(user.id)
    assert loaded is not None
    assert loaded.username == user.username
    assert loaded.email == user.email
    assert loaded.role == user.role
    assert loaded.status == user.status
    assert loaded.hashed_password == user.hashed_password
    # Eliminar usuario creado
    assert delete_user(user.id) is True
    assert load_user(user.id) is None


def test_load_all_users():
    user1 = User(
        id=str(uuid.uuid4()),
        username="user1",
        email="user1@example.com",
        role=UserRole.PLAYER,
        status=UserStatus.ACTIVE,
        hashed_password="pass1"
    )
    user2 = User(
        id=str(uuid.uuid4()),
        username="user2",
        email="user2@example.com",
        role=UserRole.ADMIN,
        status=UserStatus.BANNED,
        hashed_password="pass2"
    )
    save_user(user1)
    save_user(user2)
    users = load_all_users()
    ids = [u.id for u in users]
    assert user1.id in ids
    assert user2.id in ids
    # Eliminar usuarios creados
    assert delete_user(user1.id) is True
    assert delete_user(user2.id) is True


def test_save_and_load_game():
    game = Game(
        id=str(uuid.uuid4()),
        name="Partida Test",
        creator_id="creator1",
        players=[],
        roles={},
        status=GameStatus.WAITING,
        max_players=8
    )
    save_game(game)
    loaded = load_game(game.id)
    assert loaded is not None
    assert loaded.name == game.name
    assert loaded.creator_id == game.creator_id
    assert loaded.status == game.status
    assert loaded.max_players == game.max_players
    # Eliminar partida creada
    assert delete_game(game.id) is True


def test_load_all_games():
    game1 = Game(
        id=str(uuid.uuid4()),
        name="Game1",
        creator_id="c1",
        players=[],
        roles={},
        status=GameStatus.WAITING,
        max_players=6
    )
    game2 = Game(
        id=str(uuid.uuid4()),
        name="Game2",
        creator_id="c2",
        players=[],
        roles={},
        status=GameStatus.STARTED,
        max_players=10
    )
    save_game(game1)
    save_game(game2)
    games = load_all_games()
    ids = [g.id for g in games]
    assert game1.id in ids
    assert game2.id in ids
    # Eliminar juegos creados
    assert delete_game(game1.id) is True
    assert delete_game(game2.id) is True

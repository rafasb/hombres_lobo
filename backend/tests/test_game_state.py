from app.models.game_and_player import Game, PlayerInfo, Roles
from app.services.game_state_service import GameState


def make_game():
    p1 = PlayerInfo(player_id="p1", role=Roles.VILLAGER)
    p2 = PlayerInfo(player_id="p2", role=Roles.VILLAGER)
    g = Game(id="g1", name="G", creator_id="u", max_players=4, players={'p1': p1, 'p2': p2})
    return g


def test_living_dead_and_eliminate():
    g = make_game()
    gs = GameState("g1", g)

    assert set(gs.get_living_players()) == {"p1", "p2"}

    gs.eliminate_player("p1")
    assert set(gs.get_dead_players()) == {"p1"}
    assert set(gs.get_living_players()) == {"p2"}


def test_votes_and_most_voted():
    g = make_game()
    gs = GameState("g1", g)

    assert gs.cast_vote("p1", "p2") is True
    assert gs.get_vote_count() == {"p2": 1}

    # p2 votes p1 -> tie
    gs.cast_vote("p2", "p1")
    assert gs.get_most_voted() is None

    # eliminated player cannot vote
    gs.eliminate_player("p2")
    assert gs.cast_vote("p2", "p1") is False


def test_night_actions_and_clear():
    g = make_game()
    gs = GameState("g1", g)

    gs.set_night_action("p1", {"action": "test"})
    assert gs.night_actions.get("p1") == {"action": "test"}

    gs.clear_night_actions()
    assert gs.night_actions == {}


def test_get_player_state():
    g = make_game()
    gs = GameState("g1", g)

    ps = gs.get_player_state("p1")
    assert ps is not None
    # ps puede ser PlayerState o dict (o similar), usar getattr/indice
    pid = getattr(ps, 'player_id', None) or (ps.get('player_id') if isinstance(ps, dict) else None)
    assert pid == "p1"

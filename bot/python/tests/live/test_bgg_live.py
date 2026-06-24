"""LIVE test: hits the real Board Game Geek XML API.

Run with:  pytest -m live
A failure here means BGG search is actually broken (the reported symptom) --
either the API is down/rate-limited or its response shape changed.
"""
import pytest

from utils.bgg import get_bgg_data
from utils.game import Game

pytestmark = pytest.mark.live


async def test_bgg_exact_search_returns_a_known_game():
    game = Game("carcassonne")
    found = await get_bgg_data(game, message=None, ctx=None, exact=True)
    assert found is True, (
        "BGG exact search for 'Carcassonne' returned nothing. BGG search is "
        "broken or the XML API response shape changed."
    )
    assert game.description, "No description fetched from the BGG thing endpoint."
    assert game.bgg, "No BGG game URL was set."

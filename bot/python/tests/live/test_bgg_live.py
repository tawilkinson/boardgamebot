"""LIVE test: hits the real Board Game Geek XML API.

Run with:  pytest -m live
BGG's XML API now requires authentication, so this is skipped unless BGG_TOKEN
is set (register an app at https://boardgamegeek.com/applications). A failure
when the token IS set means BGG search is actually broken.
"""
import os

import pytest

from utils.bgg import get_bgg_data
from utils.game import Game

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        not os.getenv("BGG_TOKEN"),
        reason="BGG_TOKEN not set; the BGG XML API requires a Bearer token",
    ),
]


async def test_bgg_exact_search_returns_a_known_game():
    game = Game("carcassonne")
    found = await get_bgg_data(game, message=None, ctx=None, exact=True)
    assert found is True, (
        "BGG exact search for 'Carcassonne' returned nothing despite a token "
        "being set. BGG search is broken or the XML API response shape changed."
    )
    assert game.description, "No description fetched from the BGG thing endpoint."
    assert game.bgg, "No BGG game URL was set."

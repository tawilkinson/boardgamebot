"""Parsing tests for utils.bgg against saved BGG XML-API fixtures.

These verify our parser logic is correct for the structure the BGG XML API is
expected to return. The matching live test (tests/live/test_bgg_live.py) checks
that the real API still emits that structure.
"""
from unittest.mock import AsyncMock, MagicMock

import discord
import requests

from utils.bgg import bgg_data_from_id, get_bgg_data
from utils.game import Game


def test_bgg_data_from_id_sets_description_and_image(mock_get, load_fixture):
    mock_get({"xmlapi2/thing": load_fixture("bgg_thing.xml")})
    game = Game("carcassonne")
    assert bgg_data_from_id(game, 822) is True
    assert "tile-laying" in game.description
    assert game.image == "https://cf.geekdo-images.com/carcassonne.jpg"
    assert game.bgg == "https://boardgamegeek.com/boardgame/822/"


async def test_get_bgg_data_single_match(mock_get, load_fixture):
    mock_get(
        {
            "xmlapi2/search": load_fixture("bgg_search_single.xml"),
            "xmlapi2/thing": load_fixture("bgg_thing.xml"),
        }
    )
    game = Game("carcassonne")
    assert await get_bgg_data(game, message=None, ctx=None, exact=True) is True
    assert game.description  # populated from the thing endpoint
    assert game.bgg.endswith("/822/")


async def test_get_bgg_data_zero_matches(mock_get, load_fixture):
    mock_get({"xmlapi2/search": load_fixture("bgg_search_zero.xml")})
    game = Game("definitelynotagame")
    assert await get_bgg_data(game, message=None, ctx=None, exact=True) is False
    assert "not found on Board Game Geek" in game.description


async def test_get_bgg_data_multiple_matches_resolves_user_choice(
    mock_get, load_fixture, capsys
):
    mock_get(
        {
            "xmlapi2/search": load_fixture("bgg_search_multiple.xml"),
            "xmlapi2/thing": load_fixture("bgg_thing.xml"),
        }
    )
    game = Game("carcassonne")

    # The bot edits the placeholder message with an "ambiguous" embed...
    message = MagicMock()
    message.edit = AsyncMock()
    # ...then waits for the user to reply with a number; simulate "1".
    reply = MagicMock(content="1")
    reply.delete = AsyncMock()
    ctx = MagicMock()
    ctx.client.wait_for = AsyncMock(return_value=reply)
    ctx.channel.type = discord.ChannelType.text

    assert await get_bgg_data(game, message, ctx, exact=True) is True
    message.edit.assert_awaited()  # ambiguous-choice embed was shown
    assert game.description  # resolved choice fetched the thing endpoint
    # No stray debug print of the raw parsed XML (was bgg.py:113).
    assert capsys.readouterr().out == ""


async def test_get_bgg_data_unreachable_returns_false(raise_get):
    raise_get(requests.exceptions.ConnectionError())
    game = Game("carcassonne")
    assert await get_bgg_data(game, message=None, ctx=None, exact=True) is False

"""Command-layer tests for the games cog.

The util functions (search_web_board_game_data / get_all_games) and the
DiscordPages paginator are patched, so these verify each command's wiring:
it sends a response, calls the right util, and handles the result branches.
"""
from unittest.mock import AsyncMock, MagicMock

import pytest

import cogs.games as games_mod
from cogs.games import Games

SAMPLE_GAME = {
    "name": "Carcassonne",
    "description": "A tile-laying game.",
    "bgg": "https://boardgamegeek.com/boardgame/822/",
    "image": "http://example.com/img.png",
    "tabletopia": "[Carcassonne](http://tabletopia/carc)",
    "tts": False,
    "bga": "[Carcassonne](http://bga/carc)",
    "yucata": False,
}


@pytest.fixture
def games_cog():
    # __new__ skips __init__, which would start the 24h cache loop.
    cog = Games.__new__(Games)
    cog.bot = MagicMock()
    return cog


@pytest.fixture
def patch_paginator(monkeypatch):
    """Replace DiscordPages with a stub whose .start is awaitable."""
    paginator = MagicMock()
    paginator.start = AsyncMock()
    monkeypatch.setattr(games_mod, "DiscordPages", lambda *a, **k: paginator)
    return paginator


async def test_search_found(games_cog, interaction, monkeypatch, patch_paginator):
    search = AsyncMock(return_value=SAMPLE_GAME)
    monkeypatch.setattr(games_mod, "search_web_board_game_data", search)

    await Games.game_search.callback(games_cog, interaction, game="carcassonne")

    interaction.response.send_message.assert_awaited()  # "Searching..."
    # Searched using the capitalised name.
    assert search.await_args.args[0] == "Carcassonne"
    interaction.message.delete.assert_awaited()  # placeholder removed
    interaction.followup.send.assert_awaited()  # result embed


async def test_search_not_found(games_cog, interaction, monkeypatch):
    monkeypatch.setattr(
        games_mod, "search_web_board_game_data", AsyncMock(return_value=False)
    )

    await Games.game_search.callback(games_cog, interaction, game="nope")

    # On no result, the placeholder message is edited rather than deleted.
    interaction.message.edit.assert_awaited()
    assert "not found" in interaction.message.edit.call_args.kwargs["content"]


@pytest.mark.parametrize(
    "callback,site",
    [
        ("game_bga", 1),
        ("game_yucata", 3),
        ("game_tts", 4),
    ],
)
async def test_all_games_listings(
    games_cog, interaction, monkeypatch, patch_paginator, callback, site
):
    captured = {}

    def fake_get_all_games(site):
        captured["site"] = site
        return {"Carcassonne": "[Carcassonne](http://x/carc)"}

    monkeypatch.setattr(games_mod, "get_all_games", fake_get_all_games)

    await getattr(Games, callback).callback(games_cog, interaction)

    interaction.response.send_message.assert_awaited()
    assert captured["site"] == site
    interaction.message.delete.assert_awaited()


async def test_tabletopia_static_embed(games_cog, interaction):
    await Games.game_tabletopia.callback(games_cog, interaction)
    interaction.response.send_message.assert_awaited()
    embed = interaction.response.send_message.call_args.kwargs["embed"]
    assert "Tabletopia" in embed.title

"""Fixtures shared by the command-layer tests.

Command callbacks build embeds via GameEmbed, which calls get_discord_colour
(network image fetch + KMeans). Stub it for every command test.
"""
import discord
import pytest

import utils.embeds as embeds_mod


@pytest.fixture(autouse=True)
def stub_colour(monkeypatch):
    monkeypatch.setattr(
        embeds_mod, "get_discord_colour", lambda url: discord.Colour.blurple()
    )

"""Unit tests for utils.embeds (Discord embed formatting)."""
import discord
import pytest

import utils.embeds as embeds_mod
from utils.embeds import GameEmbed, VersionsEmbeds, embed_wordle


@pytest.fixture(autouse=True)
def stub_colour(monkeypatch):
    """get_discord_colour fetches the thumbnail and runs KMeans; stub it out."""
    monkeypatch.setattr(
        embeds_mod, "get_discord_colour", lambda url: discord.Colour.blurple()
    )


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


def _all_field_values(embed):
    return [f.value for f in embed.fields]


def test_embed_wordle_builds_fields():
    embed = embed_wordle({"Title": "body", "Second": "more"})
    assert isinstance(embed, discord.Embed)
    names = [f.name for f in embed.fields]
    assert "Title" in names and "Second" in names


def test_format_game_embed_returns_embeds():
    embeds = GameEmbed(SAMPLE_GAME).format_game_embed()
    assert len(embeds) >= 1
    assert all(isinstance(e, discord.Embed) for e in embeds)
    assert embeds[0].title == "Carcassonne"


def test_format_game_embed_marks_missing_sites():
    embeds = GameEmbed(SAMPLE_GAME).format_game_embed()
    values = _all_field_values(embeds[0])
    # tts / yucata / boite are False -> rendered as the ❌ marker.
    assert "❌" in values


def test_format_game_embed_includes_present_links():
    embeds = GameEmbed(SAMPLE_GAME).format_game_embed()
    joined = " ".join(_all_field_values(embeds[0]))
    assert "http://bga/carc" in joined


@pytest.mark.parametrize(
    "site,expected_title",
    [
        (1, "Board Game Arena Games"),
        (3, "Yucata.de Games"),
        (4, "Tabletop Simulator DLC"),
    ],
)
def test_format_all_games_embed_titles(site, expected_title):
    all_links = {
        "Carcassonne": "[Carcassonne](http://x/carc)",
        "Azul": "[Azul](http://x/azul)",
    }
    embeds = GameEmbed(site=site).format_all_games_embed(all_links)
    assert len(embeds) >= 1
    assert embeds[0].title.startswith(expected_title)


async def test_versions_embeds_format_page():
    version = {
        "title": "v1.0",
        "description": "Notes",
        "url": "https://github.com/x/releases/v1.0",
    }
    source = VersionsEmbeds([version], per_page=1)
    embed = await source.format_page(None, version)
    assert isinstance(embed, discord.Embed)
    assert embed.title == "v1.0"
    assert embed.description == "Notes"

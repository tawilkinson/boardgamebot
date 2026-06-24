"""Command-layer tests for the git cog (releases + github)."""
from unittest.mock import AsyncMock, MagicMock

import pytest

import cogs.git as git_mod
from cogs.git import Git


@pytest.fixture
def git_cog():
    return Git(MagicMock())


def test_get_release_text_parses_releases(git_cog, mock_get, load_fixture):
    mock_get({"github.com": load_fixture("github_releases.html")})
    versions = git_cog.get_release_text()
    assert len(versions) >= 1
    assert versions[0]["title"] == "0.9.13"
    assert versions[0]["url"].startswith("https://github.com")
    assert "Fixed a bug" in versions[0]["description"]


def test_get_release_text_fallback_when_unreachable(git_cog, raise_get):
    import requests

    raise_get(requests.exceptions.ConnectionError())
    versions = git_cog.get_release_text()
    assert len(versions) == 1
    assert versions[0]["title"] == "Release page not found"


async def test_releases_command_starts_paginator(git_cog, interaction, monkeypatch):
    monkeypatch.setattr(
        Git,
        "get_release_text",
        lambda self: [{"title": "v1", "description": "d", "url": "https://x"}],
    )
    paginator = MagicMock()
    paginator.start = AsyncMock()
    monkeypatch.setattr(git_mod, "DiscordPages", lambda *a, **k: paginator)

    await Git.releases.callback(git_cog, interaction)
    paginator.start.assert_awaited()


async def test_github_command_sends_embed(git_cog, interaction):
    await Git.github.callback(git_cog, interaction)
    interaction.response.send_message.assert_awaited()
    embed = interaction.response.send_message.call_args.kwargs["embed"]
    assert "GitHub" in embed.title

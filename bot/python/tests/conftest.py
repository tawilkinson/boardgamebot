"""Shared pytest fixtures and test setup for the boardgamebot suite.

Layout of the suite:
  unit/      - pure logic, no network or Discord
  parsing/   - real BeautifulSoup parsers run against saved fixtures (network mocked)
  commands/  - every command callback exercised with a mocked discord.Interaction
  live/      - @pytest.mark.live, hits real external services (deselected by default)
"""
import discord
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

# --- Path / CWD setup -------------------------------------------------------
# The package root is bot/python (the parent of this tests/ directory). The bot
# imports modules as `utils.*` / `cogs.*` and loads data files via paths
# relative to the CWD (e.g. data/words.json), so both sys.path and the working
# directory must point at the package root regardless of where pytest is run.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


FIXTURES = Path(__file__).resolve().parent / "fixtures"


class FakeResponse:
    """Minimal stand-in for requests.Response. Webpage only reads ``.text``."""

    def __init__(self, text="", status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        return None


@pytest.fixture
def load_fixture():
    """Return the text of a file in tests/fixtures/."""

    def _load(name):
        return (FIXTURES / name).read_text(encoding="utf-8")

    return _load


@pytest.fixture
def mock_get(monkeypatch):
    """Patch requests.get (used by utils.game.Webpage) to serve fixtures.

    Usage::

        mock_get("<html>")                       # same text for every URL
        mock_get({"xmlapi2/search": xml, ...})   # first matching substring wins
    """
    import utils.game as game_mod

    def install(mapping):
        def fake_get(url, *args, **kwargs):
            if isinstance(mapping, str):
                return FakeResponse(mapping)
            for needle, text in mapping.items():
                if needle in url:
                    return FakeResponse(text)
            raise AssertionError(f"No fixture mapped for URL: {url}")

        monkeypatch.setattr(game_mod.requests, "get", fake_get)
        return fake_get

    return install


@pytest.fixture
def raise_get(monkeypatch):
    """Patch requests.get to raise a given requests exception (offline sims)."""
    import utils.game as game_mod

    def install(exc):
        def fake_get(url, *args, **kwargs):
            raise exc

        monkeypatch.setattr(game_mod.requests, "get", fake_get)

    return install


@pytest.fixture(autouse=True)
def clear_scraper_caches():
    """get_all_games / search_web_board_game_data are wrapped in @cached
    TTLCaches that otherwise leak state across tests. Clear before and after."""
    from utils import online_game_search as ogs

    def _clear():
        for fn in (ogs.get_all_games, ogs.search_web_board_game_data):
            cache = getattr(fn, "cache", None)
            if cache is not None:
                cache.clear()

    _clear()
    yield
    _clear()


def make_message():
    """A fake Discord Message returned by interaction.original_response()."""
    msg = MagicMock(name="Message")
    msg.edit = AsyncMock()
    msg.delete = AsyncMock()
    msg.add_reaction = AsyncMock()
    msg.embeds = [MagicMock()]
    return msg


@pytest.fixture
def interaction():
    """A fake discord.Interaction wired with AsyncMocks for the methods the
    command callbacks use. ``interaction.message`` is the object returned by
    ``original_response()`` so tests can assert on edits/deletes."""
    inter = MagicMock(name="Interaction")
    inter.response.send_message = AsyncMock()
    inter.response.defer = AsyncMock()
    inter.followup.send = AsyncMock()

    message = make_message()
    inter.original_response = AsyncMock(return_value=message)
    inter.message = message

    inter.channel = MagicMock(name="Channel")
    inter.channel.send = AsyncMock()
    inter.channel.type = discord.ChannelType.text

    inter.user = MagicMock(name="User")
    inter.user.mention = "@tester"
    inter.user.guild_permissions.manage_guild = True

    inter.client = MagicMock(name="Client")
    inter.client.wait_for = AsyncMock()
    return inter

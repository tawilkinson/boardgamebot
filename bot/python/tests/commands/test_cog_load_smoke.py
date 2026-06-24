"""Smoke test: every extension loads and registers its app commands.

This is the broad "do all the Discord commands wire up" check -- it catches
import errors, bad decorators, and command-registration regressions across the
whole bot without exercising each callback.
"""
import discord
import pytest
from discord.ext import commands

# Mirrors startup_extensions in bot.py.
EXTENSIONS = ["fun", "games", "dice", "help", "git", "wordle"]

EXPECTED_COGS = {"fun", "games", "dice", "help", "git", "wordle"}

# A representative app command from each cog/group that must be registered.
EXPECTED_COMMANDS = {
    "roll",       # dice
    "theme",      # fun
    "thought",    # fun
    "gameboard",  # fun
    "search",     # games group
    "releases",   # git
    "github",     # git
    "play",       # wordle group
    "stats",      # wordle group
    "help",       # help
}


@pytest.fixture
async def loaded_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="bg ", intents=intents)
    bot.remove_command("help")
    for ext in EXTENSIONS:
        await bot.load_extension(f"cogs.{ext}")
    yield bot
    # The games cog starts a 24h background loop on init; cancel it so the
    # event loop can close cleanly.
    games = bot.get_cog("games")
    if games is not None:
        games.game_cacher.cancel()
    await bot.close()


async def test_all_extensions_load(loaded_bot):
    assert EXPECTED_COGS.issubset({name.lower() for name in loaded_bot.cogs})


async def test_expected_app_commands_register(loaded_bot):
    registered = {cmd.name for cmd in loaded_bot.tree.walk_commands()}
    missing = EXPECTED_COMMANDS - registered
    assert not missing, f"Missing app commands: {missing}"

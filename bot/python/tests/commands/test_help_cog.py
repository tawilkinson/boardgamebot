"""Command-layer tests for the help cog."""
from unittest.mock import MagicMock

from cogs.help import Help


async def test_help_all_lists_commands(interaction):
    bot = MagicMock()
    bot.cogs = {}
    bot.walk_commands = lambda: []
    cog = Help(bot)

    await Help.help.callback(cog, interaction, cog="all")

    interaction.response.send_message.assert_awaited()
    embed = interaction.response.send_message.call_args.kwargs["embed"]
    assert "Command Listing" in embed.title
    # In a non-private channel the bot adds the ✉ DM reaction.
    interaction.message.add_reaction.assert_awaited()


async def test_help_unknown_cog_shows_error(interaction):
    bot = MagicMock()
    bot.cogs = {}
    cog = Help(bot)

    await Help.help.callback(cog, interaction, cog="bogus")

    interaction.response.send_message.assert_awaited()
    embed = interaction.response.send_message.call_args.kwargs["embed"]
    assert embed.title == "Error!"

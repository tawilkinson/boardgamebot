"""Command-layer test for the /roll slash command."""
from unittest.mock import MagicMock

from cogs.dice import Dice


async def test_roll_sends_result(interaction):
    cog = Dice(MagicMock())
    await Dice.roll.callback(cog, interaction, roll_text="2d6")
    # Announces the roll, then sends the result to the channel.
    interaction.response.send_message.assert_awaited()
    assert "rolled" in interaction.response.send_message.call_args.args[0].lower()
    interaction.channel.send.assert_awaited()

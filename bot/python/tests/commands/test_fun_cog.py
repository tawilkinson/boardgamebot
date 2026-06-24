"""Command-layer tests for the fun cog (gameboard, theme, thought)."""
from unittest.mock import MagicMock

import pytest

from cogs.fun import Fun


@pytest.fixture
def fun_cog():
    return Fun(MagicMock())


async def test_gameboard(fun_cog, interaction):
    await Fun.gameboard.callback(fun_cog, interaction)
    interaction.response.send_message.assert_awaited()
    assert "gif" in interaction.response.send_message.call_args.args[0]


async def test_theme_combines_parts(fun_cog, interaction):
    await Fun.theme.callback(fun_cog, interaction)
    interaction.response.send_message.assert_awaited()
    msg = interaction.response.send_message.call_args.args[0]
    assert " using " in msg and " set in " in msg


async def test_thought_for_the_day(fun_cog, interaction):
    await Fun.thought_for_the_day.callback(fun_cog, interaction)
    interaction.response.send_message.assert_awaited()
    assert "THOUGHT FOR THE DAY" in interaction.response.send_message.call_args.args[0]

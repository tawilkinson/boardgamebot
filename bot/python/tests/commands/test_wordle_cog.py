"""Command-layer tests for the wordle cog (stats + a full play round)."""
from unittest.mock import AsyncMock, MagicMock

import pytest

import cogs.wordle as wordle_mod
from cogs.wordle import Wordle


@pytest.fixture
def wordle_cog():
    return Wordle(MagicMock())


async def test_stats_sends_embed(wordle_cog, interaction):
    await Wordle.wordle_stats.callback(wordle_cog, interaction, word_length=5)
    interaction.response.send_message.assert_awaited()
    embed = interaction.response.send_message.call_args.kwargs["embed"]
    assert embed.fields  # contains the stats field


async def test_play_round_correct_guess(wordle_cog, interaction, monkeypatch):
    # Pick a real 5-letter dictionary word so valid_word() passes.
    answer = next(
        w
        for w in wordle_mod.WORD_SET
        if len(w) == 5 and w.isalpha() and w.islower()
    )
    monkeypatch.setattr(wordle_mod, "get_word", lambda *a, **k: answer)

    # The player immediately guesses the correct word.
    reply = MagicMock(content=answer)
    reply.author = interaction.user
    reply.channel = interaction.channel
    interaction.client.wait_for = AsyncMock(return_value=reply)

    await Wordle.wordle_play.callback(wordle_cog, interaction, word_length=5)

    # Initial board embed sent, then the "Correct!" follow-up.
    interaction.response.send_message.assert_awaited()
    interaction.followup.send.assert_awaited()
    last = interaction.followup.send.call_args.kwargs["embed"]
    field_names = [f.name for f in last.fields]
    assert any("Correct" in n for n in field_names)

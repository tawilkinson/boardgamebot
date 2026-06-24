"""Unit tests for utils.roller.Roller (splits and dispatches dice rolls)."""
from utils.roller import Roller


def test_single_roll_returns_one_response():
    responses = Roller("1d6").roll()
    assert len(responses) == 1
    assert responses[0].endswith("\n")


def test_multiple_rolls_split_on_pipe():
    responses = Roller("1d6|1d8|1d20").roll()
    assert len(responses) == 3
    # Each multi-roll response is prefixed with the original notation.
    assert responses[0].startswith("`1d6` = ")
    assert responses[1].startswith("`1d8` = ")
    assert responses[2].startswith("`1d20` = ")


def test_multiple_rolls_use_short_string_when_long():
    # A huge roll inside a multi-roll uses the elided short string.
    responses = Roller("9999d2|1d6").roll()
    assert "+ ... +" in responses[0]

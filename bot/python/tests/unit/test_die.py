"""Unit tests for the dice-rolling logic in utils.die.Die."""
import pytest

import utils.die as die_mod
from utils.die import Die


@pytest.fixture
def fixed_randint(monkeypatch):
    """Force random.randint to return a fixed value for deterministic totals."""

    def _set(value):
        monkeypatch.setattr(die_mod.random, "randint", lambda a, b: value)

    return _set


def test_single_die_total_in_range():
    d = Die("1d6")
    assert 1 <= d.total <= 6
    assert d.get_str().endswith("\n")


def test_fixed_multiple_dice_total(fixed_randint):
    fixed_randint(4)
    d = Die("3d6")
    assert d.total == 12
    assert "**12**" in d.get_str()


def test_plus_modifier(fixed_randint):
    fixed_randint(3)
    d = Die("1d6+5")
    assert d.total == 8
    assert "+ 5" in d.get_str()


def test_minus_modifier(fixed_randint):
    fixed_randint(3)
    d = Die("1d6-1")
    assert d.total == 2
    assert "- 1" in d.get_str()


def test_keep_highest_marks_advantage(fixed_randint):
    fixed_randint(4)
    d = Die("2d20k1")
    # Two equal rolls; one kept, one struck through. Keeps the 👍 marker.
    assert "👍" in d.get_str()
    assert d.total == 4


def test_keep_lowest_marks_disadvantage(fixed_randint):
    fixed_randint(4)
    d = Die("2d20kl1")
    assert "👎" in d.get_str()
    assert d.total == 4


def test_exploding_die(monkeypatch):
    # First roll hits the max (6) and explodes, second roll (3) stops it.
    rolls = iter([6, 3])
    monkeypatch.setattr(die_mod.random, "randint", lambda a, b: next(rolls))
    d = Die("1d6!")
    assert d.exploded is True
    assert "💥" in d.get_str()
    assert d.total == 9


def test_short_string_for_huge_roll():
    d = Die("9999d2")
    # The long-form string is very large; the short string elides the middle.
    assert "+ ... +" in d.get_short_str()


def test_get_len_matches_str():
    d = Die("1d6")
    assert d.get_len() == len(d.get_str())


@pytest.mark.parametrize("bad_input", ["notdice", "d", "", "hello", "12345"])
def test_invalid_notation_is_handled_gracefully(bad_input):
    # Input the dice regex cannot match must yield the syntax-error message,
    # not raise (the /roll command would otherwise crash).
    d = Die(bad_input)
    assert "Incorrect syntax" in d.get_str()
    assert d.get_short_str() == d.get_str()

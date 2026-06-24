"""Unit tests for utils.wordle_helpers."""
import pytest

from utils.wordle_helpers import (
    check_answer,
    count_wordle_field_length,
    get_emoji_word,
    get_word,
    get_wordle_stats,
    valid_word,
)

ALPHABET = [c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]


def test_check_answer_all_correct():
    correct, wrong_len, _, squares = check_answer("crane", "CRANE", list(ALPHABET))
    assert correct is True
    assert wrong_len is False
    assert squares == "🟩🟩🟩🟩🟩"


def test_check_answer_present_and_absent():
    # Guess TABLE against word PLATE: E is correct, T/A/L present but misplaced,
    # B absent.
    correct, wrong_len, leftover, squares = check_answer(
        "table", "PLATE", list(ALPHABET)
    )
    assert correct is False
    assert wrong_len is False
    assert squares[4] == "🟩"  # E in the right place
    assert "🟦" in squares  # misplaced-but-present letters
    assert "⬛" in squares  # B is absent
    # Guessed letters are removed from the leftover alphabet.
    assert "T" not in leftover


def test_check_answer_wrong_length():
    correct, wrong_len, _, _ = check_answer("cat", "CRANE", list(ALPHABET))
    assert correct is False
    assert wrong_len is True


def test_get_emoji_word_maps_known_letters():
    mapping = {"a": ":a:", "b": ":b:"}
    assert get_emoji_word("ab", mapping) == ":a: :b:"


def test_get_emoji_word_passes_through_unknown():
    assert get_emoji_word("?", {}) == "?"


def test_valid_word():
    word_set = {"crane": 1, "plate": 1}
    assert valid_word("crane", word_set) is True
    assert valid_word("zzzzz", word_set) is False


def test_get_word_returns_member_of_right_length():
    word_set = ["apple", "beans", "crane", "ab", "longword"]
    word = get_word({}, word_set, 5)
    assert len(word) == 5
    assert word in word_set


def test_get_wordle_stats_reports_counts():
    word_set = ["apple", "beans", "crane", "ab"]
    stats = get_wordle_stats(word_set, 5)
    assert "4 English words" in stats  # total dictionary size
    assert "3 English words with 5 letters" in stats


def test_count_wordle_field_length_is_positive():
    n = count_wordle_field_length([], "a b c", "🟩🟩🟩", 1, 5)
    assert isinstance(n, int)
    assert n > 0

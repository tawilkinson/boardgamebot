"""Unit tests for utils.helpers (get_int, Site enum, data-file loaders)."""
import pytest

from utils.helpers import (
    Site,
    get_int,
    get_british_spellings_from_file,
    get_regional_indicator_letters_from_file,
    get_word_set_from_file,
)


@pytest.mark.parametrize(
    "value,expected",
    # NB: get_int does int(str(value)), so a float string like "3.9" is NOT
    # truncated -- it raises and returns None.
    [(5, 5), ("5", 5), ("-3", -3), (3.9, None), ("abc", None), (None, None), ("", None)],
)
def test_get_int(value, expected):
    assert get_int(value) == expected


def test_site_enum_values():
    assert Site.bga.value == 1
    assert Site.boite.value == 2
    assert Site.yucata.value == 3
    assert Site.tts.value == 4
    assert Site(1) is Site.bga


def test_word_set_loads():
    words = get_word_set_from_file()
    assert isinstance(words, (list, dict))
    assert len(words) > 0


def test_british_spellings_load():
    spellings = get_british_spellings_from_file()
    assert isinstance(spellings, dict)
    assert len(spellings) > 0


def test_regional_indicator_letters_load():
    letters = get_regional_indicator_letters_from_file()
    assert isinstance(letters, dict)
    # Should map at least the lowercase alphabet to emoji.
    assert "a" in letters

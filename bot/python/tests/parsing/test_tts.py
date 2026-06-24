"""Parsing tests for utils.tts (Tabletop Simulator DLC + Steam Workshop)."""
from bs4 import BeautifulSoup

from utils.game import Game
from utils.tts import get_tts_data, get_tts_dlc, get_tts_workshop


def test_get_tts_dlc_finds_matching_dlc(load_fixture):
    soup = BeautifulSoup(load_fixture("tts_dlc.html"), "html.parser")
    game = Game("carcassonne")
    dlc = get_tts_dlc(game, soup)
    assert "Carcassonne" in dlc
    assert "store.steampowered.com/app/12345" in dlc
    # The "?snr=" tracking suffix is stripped.
    assert "?snr=" not in dlc


def test_get_tts_dlc_no_match_returns_empty(load_fixture):
    soup = BeautifulSoup(load_fixture("tts_dlc.html"), "html.parser")
    game = Game("a game that is not here")
    assert get_tts_dlc(game, soup) == ""


def test_get_tts_workshop_finds_shared_file(load_fixture):
    soup = BeautifulSoup(load_fixture("tts_workshop.html"), "html.parser")
    game = Game("carcassonne")
    workshop = get_tts_workshop(game, soup)
    assert "steamcommunity.com/sharedfiles" in workshop
    assert "Carcassonne" in workshop


def test_get_tts_data_combines_dlc_and_workshop(mock_get, load_fixture):
    mock_get(
        {
            "store.steampowered.com/search": load_fixture("tts_dlc.html"),
            "steamcommunity.com/workshop": load_fixture("tts_workshop.html"),
        }
    )
    game = Game("carcassonne")
    get_tts_data(game)
    assert game.tts
    assert "Carcassonne" in game.tts
    assert "steamcommunity.com/sharedfiles" in game.tts


def test_get_tts_data_unreachable_dlc_sets_error(raise_get):
    import requests

    raise_get(requests.exceptions.ConnectionError())
    game = Game("carcassonne")
    get_tts_data(game)
    # When the store page is unreachable, the error string is stored.
    assert game.tts == "Timed Out"

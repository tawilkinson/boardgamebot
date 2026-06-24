"""Parsing tests for utils.online_game_search against saved site fixtures.

Each test feeds the real BeautifulSoup parser a fixture that encodes the page
structure the scraper expects. A failure here means our parser logic is wrong;
the live suite checks whether the real sites still match these structures.
"""
from utils.game import Game
from utils.online_game_search import (
    get_all_games,
    get_bga_data,
    get_boite_a_jeux_data,
    get_tabletopia_data,
    get_yucata_data,
    search_web_board_game_data,
    set_site_data,
)


# --- set_site_data ----------------------------------------------------------

def test_set_site_data_known_sites():
    for site in (1, 2, 3, 4):
        url, name = set_site_data(site)
        assert url and name


# --- get_all_games per site -------------------------------------------------

def test_get_all_games_bga(mock_get, load_fixture):
    mock_get({"boardgamearena.com/gamelist": load_fixture("bga_gamelist.html")})
    games = get_all_games(site=1)
    assert "Carcassonne" in games
    assert "gamepanel?game=carcassonne" in games["Carcassonne"]
    assert "Azul" in games


def test_get_all_games_boite(mock_get, load_fixture):
    mock_get({"boiteajeux.net": load_fixture("boite_regles.html")})
    games = get_all_games(site=2)
    assert "Carcassonne" in games
    assert "boiteajeux.net" in games["Carcassonne"]


def test_get_all_games_yucata(mock_get, load_fixture):
    mock_get({"yucata.de/en": load_fixture("yucata.html")})
    games = get_all_games(site=3)
    assert "Carcassonne" in games
    assert "yucata.de/en/Game/Carcassonne" in games["Carcassonne"]


def test_get_all_games_tts(mock_get, load_fixture):
    mock_get({"store.steampowered.com/search": load_fixture("tts_dlc.html")})
    games = get_all_games(site=4)
    # The "Tabletop Simulator - " prefix is stripped from the names.
    assert "Carcassonne" in games
    assert "Zombicide" in games


def test_get_all_games_unreachable_returns_error_entry(raise_get):
    import requests

    raise_get(requests.exceptions.ConnectionError())
    games = get_all_games(site=1)
    assert "All Games Error" in games


# --- per-site matching helpers (used by /games search) ----------------------

def test_get_bga_data_matches(mock_get, load_fixture):
    mock_get({"boardgamearena.com/gamelist": load_fixture("bga_gamelist.html")})
    game = Game("carcassonne")
    get_bga_data(game)
    assert game.bga
    assert "gamepanel?game=carcassonne" in game.bga


def test_get_boite_data_matches(mock_get, load_fixture):
    mock_get({"boiteajeux.net": load_fixture("boite_regles.html")})
    game = Game("carcassonne")
    get_boite_a_jeux_data(game)
    assert game.boite
    assert "boiteajeux.net" in game.boite


def test_get_yucata_data_matches(mock_get, load_fixture):
    mock_get({"yucata.de/en": load_fixture("yucata.html")})
    game = Game("carcassonne")
    get_yucata_data(game)
    assert game.yucata
    assert "yucata.de" in game.yucata


def test_get_tabletopia_data_matches(mock_get, load_fixture):
    mock_get({"tabletopia.com/playground": load_fixture("tabletopia_search.html")})
    game = Game("carcassonne")
    get_tabletopia_data(game)
    assert game.tabletopia
    assert "tabletopia.com/games/carcassonne" in game.tabletopia


def test_get_bga_data_no_match_leaves_url_false(mock_get, load_fixture):
    mock_get({"boardgamearena.com/gamelist": load_fixture("bga_gamelist.html")})
    game = Game("a totally unknown game xyz")
    get_bga_data(game)
    assert game.bga is False


# --- full search pipeline (all sources mocked) ------------------------------

async def test_search_web_board_game_data_end_to_end(mock_get, load_fixture):
    mock_get({"xmlapi2/search": load_fixture("bgg_search_single.xml"),
              "xmlapi2/thing": load_fixture("bgg_thing.xml"),
              "boardgamearena.com/gamelist": load_fixture("bga_gamelist.html"),
              "boiteajeux.net": load_fixture("boite_regles.html"),
              "yucata.de/en": load_fixture("yucata.html"),
              "tabletopia.com/playground": load_fixture("tabletopia_search.html"),
              "store.steampowered.com/search": load_fixture("tts_dlc.html"),
              "steamcommunity.com/workshop": load_fixture("tts_workshop.html"),
              })
    data = await search_web_board_game_data("Carcassonne")
    assert data is not False
    assert data["name"] == "Carcassonne"
    assert data["bgg"] == "https://boardgamegeek.com/boardgame/822/"
    assert "tile-laying" in data["description"]
    # Every online source should have resolved a link for Carcassonne.
    assert data["bga"]
    assert data["boite"]
    assert data["yucata"]
    assert data["tabletopia"]
    assert data["tts"]


async def test_search_web_board_game_data_not_on_bgg(mock_get, load_fixture):
    # Both exact and non-exact BGG searches return zero -> overall False.
    mock_get({"xmlapi2/search": load_fixture("bgg_search_zero.xml")})
    data = await search_web_board_game_data("definitelynotagame")
    assert data is False

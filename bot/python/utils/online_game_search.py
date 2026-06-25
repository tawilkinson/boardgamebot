import logging
import difflib
import json
import os
import requests
from bs4 import BeautifulSoup
from cachetools import cached, TTLCache
from utils.bgg import get_bgg_data
from utils.helpers import Site
from utils.game import Game, Webpage
from utils.tts import get_tts_data

logger = logging.getLogger("discord")

YUCATA_BASE = "https://www.yucata.de"
YUCATA_LOGIN_URL = f"{YUCATA_BASE}/Services/YucataService.svc/AuthenticateViaAjax"
YUCATA_GAMES_URL = f"{YUCATA_BASE}/en/Games"
# Yucata serves its anonymous pages to a generic UA, but send a browser-like
# one to be safe.
YUCATA_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def get_tabletopia_data(game):
    """
    Takes an object of "Game" Class and searches Tabletopia for a boardgame
    that exactly matches the Game name. Will update the Game Object with url for
    the webpage of the game on Tabletopia's website.
    """
    if logger.level >= 10:
        logger.debug(f">>> Tabletopia: {game.tabletopia_search_url}")
    tabletopia_games = []
    tabletopia_page = Webpage(game.tabletopia_search_url)
    tabletopia_directory_page = tabletopia_page.page_html
    if tabletopia_directory_page:
        search_results = tabletopia_directory_page.find_all(
            "a", class_="dropdown-menu__item dropdown-item-thumb"
        )
        for result in search_results:
            game_name = result.text.strip()
            game_tabletopia_url = result["href"]
            game_tabletopia_url = f"https://tabletopia.com{game_tabletopia_url}"
            formatted_link = f"[{game_name}]({game_tabletopia_url})"
            tabletopia_games.append(formatted_link)
        if tabletopia_games:
            game.set_tabletopia_url("\n".join(tabletopia_games))
            if logger.level >= 10:
                logger.debug(f"--> retrieved {game.name} Tabletopia data")
    else:
        game.set_tabletopia_url(tabletopia_page.error)


def get_bga_data(game):
    """
    Takes an object of "Game" Class and searches Board Game Arena for a listing
    that exactly matches the Game name. Will update the Game Object with url for
    the webpage of the game on BGA's website.
    """
    if logger.level >= 10:
        logger.debug(f">>> Board Game Arena: {game.bga_search_url}")
    all_bga = get_all_games(site=1)
    if logger.level >= 10:
        logger.debug(f">>> Board Game Arena Games: {all_bga.keys()}")
    closest_match = difflib.get_close_matches(game.name, all_bga.keys(), 1)
    if len(closest_match) > 0:
        game.set_bga_url(f"{all_bga[closest_match[0]]}")
    else:
        if logger.level >= 10:
            logger.debug(f">>> Board Game Arena {game.name} not found")


def get_yucata_data(game):
    """
    Update the Game Object with url for the webpage of the game on Yuctata's website.
    """
    if logger.level >= 10:
        logger.debug(f">>> Yucata: {game.yucata_search_url}")
    all_yucata_games = get_all_games(site=3)
    yucata_games = []
    for result in all_yucata_games:
        if game.name.lower() in result.lower():
            yucata_games.append(all_yucata_games[result])
    if yucata_games:
        game.set_yucata_url("\n".join(yucata_games))
    else:
        if logger.level >= 10:
            logger.debug(f">>> Yucata.de {game.name} not found")


def _yucata_login(session):
    """Authenticate ``session`` against Yucata using YUCATA_USER / YUCATA_PASS.

    Yucata's full game catalogue is only listed for logged-in users. Returns
    True on success. Returns False (and logs a clear message) when the
    credentials are not configured or the login is rejected, so callers can
    degrade gracefully instead of crashing.
    """
    user = os.getenv("YUCATA_USER")
    password = os.getenv("YUCATA_PASS")
    if not user or not password:
        logger.warning(
            "YUCATA_USER / YUCATA_PASS not set; Yucata games cannot be listed. "
            "Set both in your .env (or as CI secrets) to enable Yucata."
        )
        return False
    try:
        response = session.post(
            YUCATA_LOGIN_URL,
            json={"login": user, "password": password, "remember": False},
            timeout=30,
        )
    except requests.exceptions.RequestException as error:
        logger.warning(f"Yucata login request failed: {error}")
        return False
    try:
        # The WCF AJAX endpoint wraps its result as {"d": <bool>}.
        success = bool(response.json().get("d"))
    except ValueError:
        success = False
    if not success:
        logger.warning(
            "Yucata login was rejected; check YUCATA_USER / YUCATA_PASS.")
    return success


def get_yucata_games():
    """All games visible to a logged-in Yucata account, as a name -> MD-link dict.

    Logs in with a fresh session and scrapes the game links from the
    authenticated games page. Returns an empty dict (logging why) if the
    credentials are missing, login fails, or the fetch fails.
    """
    session = requests.Session()
    session.headers.update({"User-Agent": YUCATA_USER_AGENT})
    if not _yucata_login(session):
        return {}
    try:
        response = session.get(YUCATA_GAMES_URL, timeout=30)
    except requests.exceptions.RequestException as error:
        logger.warning(f"Yucata games page could not be fetched: {error}")
        return {}
    page = BeautifulSoup(response.text, "html.parser")
    all_links = {}
    for anchor in page.select('a[href^="/en/GameInfo/"]'):
        name = anchor.get_text(strip=True)
        if not name:
            continue
        link = f"{YUCATA_BASE}{anchor['href']}"
        all_links[name] = f"[{name}]({link})"
    if not all_links and logger.level >= 10:
        logger.debug(">>> Yucata: logged in but found no games on the games page")
    return all_links


_search_cache = TTLCache(maxsize=1024, ttl=86400)


async def search_web_board_game_data(
    game_name, message=None, ctx=None, depth=0, max_depth=1
):
    """Result-caching wrapper around :func:`_fetch_board_game_data`.

    Caches the awaited result keyed on the game name only.
    """
    cache_key = game_name.lower()
    if cache_key in _search_cache:
        return _search_cache[cache_key]
    game_data = await _fetch_board_game_data(
        game_name, message, ctx, depth, max_depth
    )
    if game_data:
        _search_cache[cache_key] = game_data
    return game_data


# Exposed so callers/tests can clear the result cache.
search_web_board_game_data.cache = _search_cache


async def _fetch_board_game_data(
    game_name, message=None, ctx=None, depth=0, max_depth=1
):
    """
    Will search Board Game Geek (BGG) for a board game with that name, or
    else find the next best match. If a match is found on the BGG site the name,
    description, thumbnail image of the game will be saved, and 5 different
    'online-play' sites will be searched to see if that game is available to play
    on them.

    Board game data is returned in the following JSON format.
    Site URLs are formatted for MD or Flase if no URL exists.
    {
        "name": "",
        "description": "<description>",
        "bgg": "https://boardgamegeek.com/boardgame/<ID>/<name>",
        "image": "<image_url>",
        "tabletopia": "[<name>](<tabletopia_url>)",
        "tts": "[<name>](<tts_url>)",
        "bga": "[<name>](<bga_url>)",
        "yucata": "[<name>](<yucata_url>)",
    }
    """
    game = Game(game_name.lower())
    if logger.level >= 10:
        logger.debug(f"SEARCHING WEB FOR GAME DATA: {game.name}")
    game_on_bgg = await get_bgg_data(game, message, ctx)
    if not game_on_bgg:
        possible_game = await get_bgg_data(game, message, ctx, False)
        if possible_game:
            game_on_bgg = True
        else:
            return False
    if game_on_bgg:
        get_bga_data(game)
        get_tabletopia_data(game)
        get_tts_data(game)
        get_yucata_data(game)
        game_data = game.return_game_data()
        if logger.level >= 10:
            logger.debug(f"GAME DATA FOUND:\n{game_data}")
        return game_data
    return False


def set_site_data(site):
    """
    Sets site info based in site enum
    """
    game_list = None
    site_name = None
    try:
        site_enum = Site(site)
    except ValueError:
        return game_list, site_name
    if site_enum == Site.bga:
        game_list = "https://en.boardgamearena.com/gamelist?section=all"
        site_name = "Board Game Arena"
    elif site_enum == Site.yucata:
        game_list = "https://www.yucata.de/en/"
        site_name = "Yucata.de"
    elif site_enum == Site.tts:
        game_list = "https://store.steampowered.com/search/?term=tabletop+simulator&category1=21"
        site_name = "Tabletop Simulator"
    return game_list, site_name


def get_site_search_results(site, page):
    """
    Finds all game elements depending on website
    """
    search_results = None
    try:
        site_enum = Site(site)
    except ValueError:
        return search_results
    if site_enum == Site.bga:
        script_result = page.find_all("script", type="text/javascript")
        search_results = None
        for item in script_result:
            for line in item.string.split("\n"):
                if "globalUserInfos" in line:
                    try:
                        clean_line = line.rstrip().split("=", 1)[1]
                        clean_line = clean_line[:-1]
                        search_results = json.loads(clean_line)
                        if logger.level >= 10:
                            logger.debug(">>> BGA JSON succesful load")
                    except Exception as e:
                        # Should only work for the line we _want_
                        if logger.level >= 10:
                            logger.debug(f"!!! BGA JSON error: {e}")
        search_results = search_results["game_list"]
    elif site_enum == Site.tts:
        search_results = page.find_all("div", {"class": "search_name"})
    # Yucata is handled separately
    return search_results


def get_name_and_link(site, result):
    """
    Gets name and game links from different websites
    """
    name = None
    try:
        site_enum = Site(site)
    except ValueError:
        return name, ""
    if site_enum == Site.bga:
        game_href = result["name"]
        name = result["display_name_en"]
        link = f"https://boardgamearena.com/gamepanel?game={game_href}"
    elif site_enum == Site.tts:
        name = result.text.lstrip("\n").rstrip("\n ")
        link = result.parent.parent["href"]
        link = link.split("?snr=")[0]
    if "Tabletop Simulator - " in name:
        name = name.replace("Tabletop Simulator - ", "")
    return name, link


@cached(cache=TTLCache(maxsize=1024, ttl=86400))
def get_all_games(site):
    """
    Simple wrapper to get all games from each service
    """
    game_list, site_name = set_site_data(site)
    if site_name is None:
        return {}

    if Site(site) == Site.yucata:
        return get_yucata_games()

    if logger.level >= 10:
        logger.debug(f">>> {site_name} all games: {game_list}")
    all_games_page = Webpage(game_list)
    page = all_games_page.page_html

    all_links = {}
    if page is None:
        all_links["All Games Error"] = all_games_page.error
        return all_links

    search_results = get_site_search_results(site, page)

    for result in search_results:
        name, link = get_name_and_link(site, result)
        if name:
            all_links[f"{name}"] = f"[{name}]({link})"

    if logger.level >= 10:
        logger.debug(f"--> all games:\n{all_links}")
    return all_links

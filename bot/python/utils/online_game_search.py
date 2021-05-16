import logging
import difflib
import string
from cachetools import cached, TTLCache
from utils.bgg import get_bgg_data
from utils.game import Game, Webpage

logger = logging.getLogger('discord')


def get_boite_a_jeux_data(game):
    '''
    Takes an object of "Game" Class and searches Boîte à Jeux "all games" webpage
    to see if the game's name is listed. Will update the Game Object with url for
    the webpage of the game on Boîte à Jeux's website.
    '''
    if logger.level >= 10:
        logger.debug(f'>>> Boîte à Jeux: {game.boite_search_url}')
    boite_page = Webpage(game.boite_search_url)
    boite_directory_page = boite_page.page_html
    if boite_directory_page:
        search_results = boite_directory_page.find_all(
            'div', class_='jeuxRegles')
        for res in search_results:
            if game.name.lower() in res.text.lower():
                rules_elem = res.select_one('a', text='Rules')
                rules_href = rules_elem.get('href')
                game_boite_url = f'http://www.boiteajeux.net/{rules_href}'
                game.set_boite_url(
                    f'[{game.name}]({game_boite_url})')
    else:
        game.set_boite_url(boite_page.error)


def get_tabletopia_data(game):
    '''
    Takes an object of "Game" Class and searches Tabletopia for a boardgame
    that exactly matches the Game name. Will update the Game Object with url for
    the webpage of the game on Tabletopia's website.
    '''
    if logger.level >= 10:
        logger.debug(f'>>> Tabletopia: {game.tabletopia_search_url}')
    tabletopia_games = []
    tabletopia_page = Webpage(game.tabletopia_search_url)
    tabletopia_directory_page = tabletopia_page.page_html
    if tabletopia_directory_page:
        search_results = tabletopia_directory_page.find_all(
            'a', class_='dropdown-menu__item dropdown-item-thumb')
        for result in search_results:
            game_name = result.text.strip()
            game_tabletopia_url = result['href']
            game_tabletopia_url = f'https://tabletopia.com{game_tabletopia_url}'
            formatted_link = f'[{game_name}]({game_tabletopia_url})'
            tabletopia_games.append(formatted_link)
        if tabletopia_games:
            game.set_tabletopia_url('\n'.join(tabletopia_games))
            if logger.level >= 10:
                logger.debug(f'--> retrieved {game.name} Tabletopia data')
    else:
        game.set_tabletopia_url(tabletopia_page.error)


def get_tts_data(game):
    '''
    Takes an object of "Game" Class and searches Steam for a Tabletop Simulator
    script that exactly matches the Game name.
    Will update the Game Object with url for the webpage of the game on steam website.
    '''
    if logger.level >= 10:
        logger.debug(f'>>> Tabletop Simulator: {game.tts_search_url}')
    tts_dlc_page = Webpage(game.tts_dlc_url)
    tts_dlc_search = tts_dlc_page.page_html
    if tts_dlc_search:
        dlc_results = tts_dlc_search.find_all(
            'div', {'class': 'search_name'})
        dlc = ''
        for result in dlc_results:
            this_name = result.text.lstrip('\n').rstrip('\n ')
            if game.name.lower() in this_name.lower():
                url = result.parent.parent['href']
                url = url.split('?snr=')[0]
                dlc = f'[{this_name}]({url})'
                dlc = (f'[{game.name} (DLC)]({url})\n')
                if logger.level >= 10:
                    logger.debug(
                        f'--> retrieved {game.name} Tabletop Simulator DLC data')
                break
        tts_search = Webpage(game.tts_search_url).page_html
        search_results = tts_search.body.select('body a')
        workshop = ''
        #
        for result in search_results:
            url = result['href']
            try:
                if 'https://steamcommunity.com/sharedfiles' in url:
                    url_name = result.contents[0].contents[0]
                    match_factor = difflib.SequenceMatcher(
                        None, game.name, url_name).ratio()
                    if logger.level >= 10:
                        logger.debug(
                            f'>>> {game.name} vs. {url_name} ={match_factor}')
                    if (match_factor > 0.5) or (game.name in url_name):
                        url = url.replace(
                            '/url?q=',
                            '').replace(
                            '%3F',
                            '?').replace(
                            '%3D',
                            '=').split('&')[0]
                        workshop += f'[{url_name}]({url})\n'
                        if logger.level >= 10:
                            logger.debug(
                                f'--> retrieved {url_name} Tabletop Simulator Steam Workshop data')
            except AttributeError:
                if logger.level >= 10:
                    logger.debug(
                        f'--> No url_name')
        if workshop:
            if workshop[-1:] == '\n':
                workshop = workshop[:-1]
        game.set_tts_url(f'{dlc}{workshop}')
    else:
        game.set_tts_url(tts_dlc_page.error)


def get_bga_data(game):
    '''
    Takes an object of "Game" Class and searches Board Game Arena for a listing
    that exactly matches the Game name. Will update the Game Object with url for
    the webpage of the game on BGA's website.
    '''
    if logger.level >= 10:
        logger.debug(f'>>> Board Game Arena: {game.bga_search_url}')
    bga_page = Webpage(game.bga_search_url)
    bga_search_page = bga_page.page_html
    if bga_search_page:
        bga_page_text = bga_search_page.body.text
        if 'Sorry, an unexpected error has occurred...' not in bga_page_text:
            game.set_bga_url(f'[{game.name}]({game.bga_search_url})')
            if logger.level >= 10:
                logger.debug(
                    f'--> retrieved {game.name} Board Game Arena data')
        else:
            if logger.level >= 10:
                logger.debug(
                    f'>>> Board Game Arena: {game.bga_non_exact_search_url}')
            all_bga = get_all_games(
                bga=True, boite=False, tts=False, yucata=False)
            closest_match = difflib.get_close_matches(
                game.name, all_bga.keys(), 1)
            if len(closest_match) > 0:
                game.set_bga_url(f'{all_bga[closest_match[0]]}')
    else:
        game.set_bga_url(bga_page.error)


def get_yucata_data(game):
    '''
    Update the Game Object with url for the webpage of the game on Yuctata's website.
    '''
    if logger.level >= 10:
        logger.debug(f'>>> Yucata: {game.yucata_search_url}')
    all_yucata_games = get_all_games(
        bga=False, boite=False, tts=False, yucata=True)
    yucata_games = []
    for result in all_yucata_games:
        if game.name.lower() in result.lower():
            yucata_games.append(all_yucata_games[result])
    if yucata_games:
        game.set_yucata_url('\n'.join(yucata_games))
        if logger.level >= 10:
            logger.debug(f'--> retrieved {game.name} Yucata data')
    else:
        game.set_yucata_url('No Game Data')


@cached(cache=TTLCache(maxsize=1024, ttl=86400))
async def search_web_board_game_data(game_name, message=None, ctx=None, depth=0, max_depth=1):
    '''
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
        "boite": "[<name>](<boite_url>)",
    }
    '''
    game = Game(game_name.lower())
    if logger.level >= 10:
        logger.debug(f'SEARCHING WEB FOR GAME DATA: {game.name}')
    game_on_bgg = await get_bgg_data(game, message, ctx)
    if not game_on_bgg:
        possible_game = await get_bgg_data(game, message, ctx, False)
        if possible_game:
            game_on_bgg = True
        else:
            return False
    if game_on_bgg:
        get_bga_data(game)
        get_boite_a_jeux_data(game)
        get_tabletopia_data(game)
        get_tts_data(game)
        get_yucata_data(game)
        game_data = game.return_game_data()
        if logger.level >= 10:
            logger.debug(f'GAME DATA FOUND:\n{game_data}')
        return game_data
    return False


@cached(cache=TTLCache(maxsize=1024, ttl=86400))
def get_all_games(bga=False, boite=False, tts=False, yucata=False):
    '''
    Simple wrapper to get all games from each service
    '''
    if not bga and boite and tts and yucata:
        if logger.level >= 10:
            logger.debug(f'get_all_games() called with no website set!')
        return {}
    if bga:
        game_list = 'https://boardgamearena.com/gamelist?section=all'
        bga_base_url = 'https://boardgamearena.com'
        name = 'Board Game Arena'
    if boite:
        game_list = 'http://www.boiteajeux.net/index.php?p=regles'
        name = 'Boîte à Jeux'
    if yucata:
        game_list = 'https://www.yucata.de/en/'
        name = 'Yucata.de'
    if tts:
        game_list = 'https://store.steampowered.com/search/?term=tabletop+simulator&category1=21'
        name = 'Tabletop Simulator'
    if logger.level >= 10:
        logger.debug(f'>>> {name} all games: {game_list}')
    all_games_page = Webpage(game_list)
    page = all_games_page.page_html
    all_links = {}
    if page:
        if bga:
            search_results = page.find_all(
                'div', class_='gameitem_baseline gamename')
        if boite:
            search_results = page.find_all('div', class_='jeuxRegles')
        if yucata:
            search_results = page.find_all('a', class_='jGameInfo')
        if tts:
            search_results = page.find_all('div', {'class': 'search_name'})
        for result in search_results:
            if bga:
                name = str(result.contents[0]).lstrip().rstrip()
                link = bga_base_url + result.parent.get('href')
            elif boite:
                rules_elem = result.select_one('a', text='Rules')
                rules_href = rules_elem.get('href')
                link = f'http://www.boiteajeux.net/{rules_href}'
                name = string.capwords(
                    str(result.contents[0]).lstrip().rstrip())
            elif yucata:
                game_href = result['href']
                name = result.text
                link = f'https://www.yucata.de{game_href}'
            elif tts:
                name = result.text.lstrip('\n').rstrip('\n ')
                link = result.parent.parent['href']
                link = link.split('?snr=')[0]
            if name:
                if 'Tabletop Simulator - ' in name:
                    name = name.replace('Tabletop Simulator - ', '')
                all_links[f'{name}'] = f'[{name}]({link})'
    else:
        all_links['All Games Error'] = all_games_page.error
    if logger.level >= 10:
        logger.debug(f'--> all games:\n{all_links}')
    return all_links

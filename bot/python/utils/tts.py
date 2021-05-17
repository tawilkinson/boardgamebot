import logging
import difflib
from utils.game import Webpage

logger = logging.getLogger('discord')


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
    # If this fails return the error
    if tts_dlc_search is None:
        game.set_tts_url(tts_dlc_page.error)
        return
    # DLC search
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
    # If this fails return what we have so far
    if tts_search is None:
        game.set_tts_url(f'{dlc}')
        return
    # TTS Scripts search
    search_results = tts_search.body.select('body a')
    workshop = ''
    for result in search_results:
        url = result['href']
        url_name = None
        try:
            if 'https://steamcommunity.com/sharedfiles' in url:
                url_name = result.contents[0].contents[0]
        except AttributeError:
            if logger.level >= 10:
                logger.debug(
                    f'--> No url_name')

        if url_name:
            match_factor = difflib.SequenceMatcher(
                None, game.name, url_name).ratio()
            if logger.level >= 10:
                logger.debug(
                    f'>>> {game.name} vs. {url_name} = {match_factor:02f}')
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

    if workshop:
        if workshop[-1:] == '\n':
            workshop = workshop[:-1]
    game.set_tts_url(f'{dlc}{workshop}')

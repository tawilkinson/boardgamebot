import asyncio
import collections
import discord
import lxml
import html
import requests
import time
import difflib
import requests_cache
import string
from bs4 import BeautifulSoup

logger = logging.getLogger('discord')

requests_cache.install_cache(
    cache_name='cache',
    backend='memory',
    expire_after=86400,
    allowable_codes=(200, ),
    allowable_methods=('GET', ),
    old_data_on_error=False,
)


class Webpage(BeautifulSoup):
    '''
    Creates a BeautifulSoup object of a webpages's HTML.
    '''

    def __init__(self, url):
        try:
            self.response = requests.get(url)
            self.page_response = self.response
            self.page_html = BeautifulSoup(self.response.text, 'lxml')
            self.error = None
        except requests.exceptions.SSLError:
            self.page_response = None
            self.page_html = None
            self.error = 'SSL Error'
        except requests.exceptions.HTTPError:
            self.page_response = None
            self.page_html = None
            self.error = 'HTTP Error'
        except requests.exceptions.HTTPError:
            self.page_response = None
            self.page_html = None
            self.error = 'Timed Out'


class Game:
    '''
    When a new Game class is created, site-specific urls are autogenerated for boardgamearena.com, boardgamegeek.com,
    boiteajeux.net, tabletopia.com, steamcommunity.com (for table top simulator games) and yucata.de.
    Class methods exist to update the Game the attribuites that are initialised as 'False' with data.
    Class method `return_game_data` formats the Game data as a dictionary.
    '''

    def __init__(self, name):
        self.name = string.capwords(name)
        self.search_name = self.name.lower().replace(' ', '%20')
        self.search_name_alpha_num = ''.join(
            [x for x in self.name.lower() if x.isalpha()])
        self.app = ''
        self.bga = False
        self.bga_search_url = f'https://boardgamearena.com/gamepanel?game={self.search_name_alpha_num}'
        self.bga_non_exact_search_url = f'https://boardgamearena.com/gamelist?section=all'
        self.bgg = ''
        self.bgg_search_url = f'http://www.boardgamegeek.com/xmlapi2/search?query={self.search_name}&exact=1&type=boardgame'
        self.bgg_non_exact_search_url = f'http://www.boardgamegeek.com/xmlapi2/search?query={self.search_name}&type=boardgame'
        self.boite = False
        self.boite_search_url = 'http://www.boiteajeux.net/index.php?p=regles'
        self.description = False
        self.image = ''
        self.tabletopia = ''
        self.tabletopia_search_url = f'https://tabletopia.com/playground/playgroundsearch/search?timestamp={int(time.time() * 1000)}&query={self.search_name}'
        self.tts = False
        self.tts_dlc_url = 'https://store.steampowered.com/search/?term=tabletop+simulator&category1=21'
        self.tts_search_url = f'https://steamcommunity.com/workshop/browse/?appid=286160&searchtext="{self.name}"&browsesort=textsearch&section=readytouseitems&requiredtags%5B0%5D=Game&actualsort=textsearch&p=1'
        self.yucata = False
        self.yucata_search_url = 'https://www.yucata.de/en/'

    def update_name(self, new_name):
        self.name = string.capwords(new_name)
        self.search_name = self.name.lower().replace(' ', '%20')
        self.search_name_alpha_num = ''.join(
            [x for x in self.name.lower() if x.isalpha()])

    def set_description(self, description):
        self.description = description

    def set_image(self, description):
        self.image = description

    def set_bga_url(self, url):
        self.bga = url

    def set_boite_url(self, url):
        self.boite = url

    def set_tabletopia_url(self, url):
        self.tabletopia = url

    def set_tts_url(self, tts):
        self.tts = tts

    def set_yucata_url(self, url):
        self.yucata = url

    def get_set_bgg_url(self, game_id):
        self.bgg = f'https://boardgamegeek.com/boardgame/{game_id}/'
        return f'http://www.boardgamegeek.com/xmlapi2/thing?id={game_id}'

    def return_game_data(self):
        return dict(
            name=self.name,
            description=self.description,
            bgg=self.bgg,
            image=self.image,
            tabletopia=self.tabletopia,
            tts=self.tts,
            bga=self.bga,
            yucata=self.yucata,
            boite=self.boite,
            app=self.app,
        )


def get_boite_a_jeux_data(game, debug=False):
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


def bgg_data_from_id(game, game_id, debug=False):
    '''
    Takes an item of Game class and a known BGG id. Sets relevant
    game data from the BGG page referenced by id.
    '''
    bgg_url = game.get_set_bgg_url(game_id)
    if logger.level >= 10:
        logger.debug(f'>>> {game.name} on BGG: {bgg_url}')
    bgg_page = Webpage(bgg_url)
    if bgg_page.page_html.items.description:
        game_description = html.unescape(
            bgg_page.page_html.items.description.text)
        abridged_game_description = f'{game_description[0:300]} ...'
        game.set_description(abridged_game_description)
        if logger.level >= 10:
            logger.debug(f'--> retrieved {game.name} description')
        if bgg_page.page_html.items.image:
            game_image = bgg_page.page_html.items.image.text
            game.set_image(game_image)
            if logger.level >= 10:
                logger.debug(f'--> retrieved {game.name} image')
        if logger.level >= 10:
            logger.debug(f'--> retrieved {game.name} Board Game Geek data')
        return True
    return False


async def get_bgg_data(game, message, ctx, exact=True, debug=False):
    '''
    Takes an object of "Game" Class and searches Board Game Geeks API for a boardgame
    that exactly matches the Game name. Will update the Game Object with url for
    the webpage of the game on BBGs website, as well as the Game's image, and description.
    '''
    game_id = 0
    if exact:
        if logger.level >= 10:
            logger.debug(f'>>> Board Game Geek: {game.bgg_search_url}')
        bgg_search = Webpage(game.bgg_search_url)
    else:
        if logger.level >= 10:
            logger.debug(
                f'>>> Board Game Geek: {game.bgg_non_exact_search_url}')
        bgg_search = Webpage(game.bgg_non_exact_search_url)
    if bgg_search.page_html:
        if bgg_search.page_html.items is not None:
            games_found = bgg_search.page_html.items['total']

            if games_found == '0':
                game.set_description(
                    'Game not found on Board Game Geek! Is it even a board game?')
                if logger.level >= 10:
                    logger.debug(
                        f'!!! {game.name} not found on Board Game Geek !!!')
            elif int(games_found) > 1:
                closest_match = None
                board_game_search = bgg_search.page_html.items.findAll('item')
                possible_board_games = collections.OrderedDict()
                count = 0
                title = 'Ambiguous Game Name'
                description = ''
                response = discord.Embed(
                    title=title,
                    description=description,
                    colour=discord.Colour.dark_purple())
                for game_search in board_game_search:
                    count += 1
                    possible_name = game_search.find('name').get(
                        'value')
                    possible_year = game_search.find('yearpublished').get(
                        'value')
                    possible_board_games[game_search['id']] = {
                        'name': possible_name, 'year': possible_year}
                    name = f'{count}: {possible_name}'
                    value = f'{possible_year}'
                    if (len(response) + len(name) + len(value)) > 5999:
                        break
                    else:
                        response.add_field(name=name, value=value)
                description = f'{len(possible_board_games)} potential matches on Board Game Geek.'
                description += '\nPlease respond with the number of the game you were looking for...'
                response.description = description
                if logger.level >= 10:
                    logger.debug(
                        f'--> found {len(possible_board_games)} potential matches on Board Game Geek')
                difflib_closest = difflib.get_close_matches(
                    game.name, possible_board_games.keys(), 1, 0)[0]
                await message.edit(content='', embed=response)

                if ctx:
                    def check(m):
                        '''
                        Checks message is by original command user, in the same channel
                        and is a number
                        '''
                        try:
                            _ = int(m.content)
                            is_int = True
                        except ValueError:
                            is_int = False
                        return is_int and m.channel == ctx.channel and m.author == ctx.author
                    try:
                        msg = await ctx.bot.wait_for('message', timeout=30, check=check)
                        if msg:
                            idx = int(msg.content) - 1
                            key = list(possible_board_games.keys())[idx]
                            closest_match = possible_board_games[key]['name']
                            game.update_name(closest_match)
                            if ctx.channel.type is not discord.ChannelType.private:
                                await msg.delete()
                        else:
                            game.update_name(difflib_closest)
                            closest_match = difflib_closest
                    except asyncio.TimeoutError:
                        game.update_name(difflib_closest)
                        closest_match = difflib_closest
                if closest_match:
                    if logger.level >= 10:
                        logger.debug(f'--> {closest_match} is closest match')
                    if key:
                        return bgg_data_from_id(game, key)
                    game.update_name(closest_match)
                    game_id = possible_board_games[closest_match]['id']
                    return bgg_data_from_id(game, game_id)
                return False
            else:
                game_id = bgg_search.page_html.items.item['id']
                return bgg_data_from_id(game, game_id)
        else:
            if ctx and exact:
                await ctx.send('BBG Unreachable. Is BGG online?')
    if logger.level >= 10:
        logger.debug(f'--> {bgg_search.error}')
    return False


def get_tabletopia_data(game, debug=False):
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


def get_tts_data(game, debug=False):
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
                if debug:
                    print(
                        f'--> No url_name')
        if workshop:
            if workshop[-1:] == '\n':
                workshop = workshop[:-1]
        game.set_tts_url(f'{dlc}{workshop}')
    else:
        game.set_tts_url(tts_dlc_page.error)


def get_bga_data(game, debug=False):
    '''
    Takes an object of "Game" Class and searches Board Game Arena for a listing
    that exactly matches the Game name. Will update the Game Object with url for
    the webpage of the game on BGA's website.
    '''
    if logger.level >= 10:
        logger.debug(f'> Board Game Arena: {game.bga_search_url}')
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
            bga_page = Webpage(game.bga_non_exact_search_url)
            bga_search_page = bga_page.page_html
            if bga_search_page:
                search_results = bga_search_page.find_all(
                    'div', class_='gameitem_baseline gamename')
                games = {}
                for result in search_results:
                    name = str(result.contents[0]).lstrip().rstrip()
                    games[name] = result
                bga_base_url = f'https://boardgamearena.com'
                closest_match = difflib.get_close_matches(
                    game.name, games.keys(), 1)
                if len(closest_match) > 0:
                    name = str(
                        games[closest_match[0]].contents[0]).lstrip().rstrip()
                    link = bga_base_url + \
                        games[closest_match[0]].parent.get('href')
                    game.set_bga_url(f'[{name}]({link})')
    else:
        game.set_bga_url(bga_page.error)


def get_yucata_data(game, debug=False):
    '''
    Takes an object of "Game" Class and searches Yucata for a listing
    that exactly matches the Game name. Will update the Game Object with url for
    the webpage of the game on Yuctata's website.
    '''
    if logger.level >= 10:
        logger.debug(f'>>> Yucata: {game.yucata_search_url}')
    yucata_games = []
    yucata_page = Webpage(game.yucata_search_url)
    yucata_directory_page = yucata_page.page_html
    if yucata_directory_page:
        search_results = yucata_directory_page.find_all(
            'a', class_='jGameInfo')
        for res in search_results:
            if game.name.lower() in res.text.lower():
                game_href = res['href']
                game_name = res.text
                game_yucata_url = f'https://www.yucata.de{game_href}'
                formatted_link = f'[{game_name} on Yucata]({game_yucata_url})'
                yucata_games.append(formatted_link)
        if yucata_games:
            game.set_yucata_url('\n'.join(yucata_games))
            if logger.level >= 10:
                logger.debug(f'--> retrieved {game.name} Yucata data')
    else:
        game.set_yucata_url(yucata_page.error)


async def search_web_board_game_data(game_name, message=None, ctx=None, debug=False, depth=0, max_depth=1):
    '''
    Willwill search Board Game Geek (BGG) for a board game with that name, or
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
    game_on_bgg = await get_bgg_data(game, message, ctx, debug=debug)
    if not game_on_bgg:
        possible_game = await get_bgg_data(game, message, ctx, False, debug)
        if possible_game:
            game_on_bgg = True
        else:
            return False
    if game_on_bgg:
        get_bga_data(game, debug)
        get_boite_a_jeux_data(game, debug)
        get_tabletopia_data(game, debug)
        get_tts_data(game, debug)
        get_yucata_data(game, debug)
        game_data = game.return_game_data()
        if logger.level >= 10:
            logger.debug(f'GAME DATA FOUND:\n{game_data}')
        return game_data
    return False


def get_all_games(bga, boite, tts, yucata, debug=False):
    '''
    Simple wrapper to get all games from each service
    '''
    if bga:
        game_list = 'https://boardgamearena.com/gamelist?section=all'
        bga_base_url = 'https://boardgamearena.com'
    if boite:
        game_list = 'http://www.boiteajeux.net/index.php?p=regles'
    if yucata:
        game_list = 'https://www.yucata.de/en/'
    if tts:
        game_list = 'https://store.steampowered.com/search/?term=tabletop+simulator&category1=21'
    if logger.level >= 10:
        logger.debug(f'>>> Board Game Arena all games: {game_list}')
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

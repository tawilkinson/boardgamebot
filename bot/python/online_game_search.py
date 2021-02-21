import lxml
import json
import html
import requests
import time
import difflib
import requests_cache
from bs4 import BeautifulSoup

requests_cache.install_cache(
    cache_name='cache',
    backend='memory',
    expire_after=86400,
    allowable_codes=(200, ),
    allowable_methods=('GET', ),
    old_data_on_error=False,
)


class Webpage(BeautifulSoup):
    """
    Creates a BeautifulSoup object of a webpages's HTML.
    """

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
    """
    When a new Game class is created, site-specific urls are autogenerated for boardgamearena.com, boardgamegeek.com,
    boiteajeux.net, tabletopia.com, steamcommunity.com (for table top simulator games) and yucata.de.
    Class methods exist to update the Game the attribuites that are initialised as 'False' with data.
    Class method `return_game_data` formats the Game data as a dictionary.
    """

    def __init__(self, name):
        self.name = name.title()
        self.search_name = self.name.lower().replace(' ', '%20')
        self.search_name_alpha_num = ''.join(
            [x for x in self.name.lower() if x.isalpha()])
        self.app = ''
        self.bga = False
        self.bga_search_url = f'https://boardgamearena.com/gamepanel?game={self.search_name_alpha_num}'
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

    def get_set_bgg_url(self, id):
        self.bgg = f'https://boardgamegeek.com/boardgame/{id}/'
        return f'http://www.boardgamegeek.com/xmlapi2/thing?id={id}'

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
    """
    Takes an object of "Game" Class and searches Boite a Jeux "all games" webpage
    to see if the game's name is listed. Will update the Game Object with url for
    the webpage of the game on Boite a Jeux's website.
    """
    if debug:
        print(f'> Boite a Jeux: {game.boite_search_url}')
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
                    f'[{game.name} on Boite a Jeux]({game_boite_url}')
    else:
        game.set_boite_url(boite_page.error)


def get_bgg_data(game, debug=False):
    """
    Takes an object of "Game" Class and searches Board Game Geeks API for a boardgame
    that exactly matches the Game name. Will update the Game Object with url for
    the webpage of the game on BBGs website, as well as the Game's image, and description.
    """
    if debug:
        print(f'> Board Game Geek: {game.bgg_search_url}')
    bgg_search = Webpage(game.bgg_search_url)
    if bgg_search.page_html:
        games_found = bgg_search.page_html.items['total']

        if games_found == '0':
            game.set_description(
                'Game not found on Board Game Geek! Is it even a board game?')
            if debug:
                print(f'> !!! {game.name} not found on Board Game Geek !!!')
            return False

        else:
            id = bgg_search.page_html.items.item['id']
            bbg_url = game.get_set_bgg_url(id)
            if debug:
                print(f'> {game.name} on BGG: {bbg_url}')
            bgg_page = Webpage(bbg_url)
            if bgg_page.page_html.items.description:
                game_description = html.unescape(
                    bgg_page.page_html.items.description.text)
                abridged_game_description = f'{game_description[0:300]} ...'
                game.set_description(abridged_game_description)
                if debug:
                    print(f'--> retrieved {game.name} description')
            if bgg_page.page_html.items.image:
                game_image = bgg_page.page_html.items.image.text
                game.set_image(game_image)
                if debug:
                    print(f'--> retrieved {game.name} image')
            if debug:
                print(f'--> retrieved {game.name} Board Game Geek data')
            return True
    else:
        if debug:
            print(f'--> {bgg_search.error}')
        return False


def get_non_exact_bgg_data(game, debug=False):
    """
    Takes an object of "Game" Class and searches Board Game Geeks API for a boardgame
    that best matches the Game name. Will return the BGG name of the best match, or
    False if no match is found.
    """
    if debug:
        print(f'> Board Game Geek: {game.bgg_non_exact_search_url}')
    bgg_search = Webpage(game.bgg_non_exact_search_url)
    if bgg_search.page_html:
        games_found = bgg_search.page_html.items['total']

        if games_found == '0':
            game.set_description(
                'Game not found on Board Game Geek! Is it even a board game?')
            if debug:
                print(
                    f'> !!! No potential matches for {game.name} found on Board Game Geek !!!')
            return False

        else:
            board_game_search = bgg_search.page_html.items.findAll('item')
            possible_board_games = [game_search.find('name').get(
                'value') for game_search in board_game_search]
            if debug:
                print(
                    f'--> found {len(possible_board_games)} potential matches on Board Game Geek')
            closest_match = difflib.get_close_matches(
                game.name, possible_board_games, 1, 0)[0]
            if debug:
                print(f'--> {closest_match} is closest match')
            return closest_match
    else:
        if debug:
            print(f'--> {bgg_search.error}')
        return False


def get_tabletopia_data(game, debug=False):
    """
    Takes an object of "Game" Class and searches Tabletopia for a boardgame
    that exactly matches the Game name. Will update the Game Object with url for
    the webpage of the game on Tabletopia's website.
    """
    if debug:
        print(f'> Tabletopia: {game.tabletopia_search_url}')
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
            formatted_link = f'[{game_name} on Tabletopia]({game_tabletopia_url})'
            tabletopia_games.append(formatted_link)
        if tabletopia_games:
            game.set_tabletopia_url('\n'.join(tabletopia_games))
            if debug:
                print(f'--> retrieved {game.name} Tabletopia data')
    else:
        game.set_tabletopia_url(tabletopia_page.error)


def get_tts_data(game, debug=False):
    """
    Takes an object of "Game" Class and searches Steam for a Tabletop Simulator
    script that exactly matches the Game name.
    Will update the Game Object with url for the webpage of the game on steam website.
    """
    if debug:
        print(f'> Tabletop Simulator: {game.tts_search_url}')
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
                dlc = (f"[ {game.name} on Tabletop Simulator]({url})\n")
                if debug:
                    print(
                        f'--> retrieved {game.name} Tabletop Simulator DLC data')
                break
        tts_search = Webpage(game.tts_search_url).page_html
        search_results = tts_search.body.select('body a')
        workshop = ''
        for result in search_results:
            url = result['href']
            try:
                if 'https://steamcommunity.com/sharedfiles' in url:
                    url_name = result.contents[0].contents[0]
                    url = url.replace(
                        '/url?q=',
                        '').replace(
                        '%3F',
                        '?').replace(
                        '%3D',
                        '=').split('&')[0]
                    workshop += f"\n[{url_name} on Steam Workshop]({url})"
                    if debug:
                        print(
                            f'--> retrieved {url_name} Tabletop Simulator Steam Workshop data')
            except AttributeError:
                if debug:
                    print(
                        f'--> No url_name')

        game.set_tts_url(f"{dlc}{workshop}")
    else:
        game.set_tts_url(tts_dlc_page.error)


def get_bga_data(game, debug=False):
    """
    Takes an object of "Game" Class and searches Board Game Arena for a listing
    that exactly matches the Game name. Will update the Game Object with url for
    the webpage of the game on BGA's website.
    """
    if debug:
        print(f'> Board Game Arena: {game.bga_search_url}')
    bga_page = Webpage(game.bga_search_url)
    bga_search_page = bga_page.page_html
    if bga_search_page:
        bga_page_text = bga_search_page.body.text
        if 'Sorry, an unexpected error has occurred...' not in bga_page_text:
            game.set_bga_url(f'[{game.name} on BGA]({game.bga_search_url})')
            if debug:
                print(f'--> retrieved {game.name} Board Game Arena data')
    else:
        game.set_bga_url(bga_page.error)


def get_yucata_data(game, debug=False):
    """
    Takes an object of "Game" Class and searches Yucata for a listing
    that exactly matches the Game name. Will update the Game Object with url for
    the webpage of the game on Yuctata's website.
    """
    if debug:
        print(f'> Yucata: {game.yucata_search_url}')
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
            if debug:
                print(f'--> retrieved {game.name} Yucata data')
    else:
        game.set_yucata_url(yucata_page.error)


def search_web_board_game_data(game_name, debug=False):
    """
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
        "tabletopia": "[<name> on Tabletopia](<tabletopia_url>)",
        "tts": "[<name> on Tabletop Simulator](<tts_url>)",
        "bga": "[<name> on BGA](<bga_url>)",
        "yucata": "[<name> on Yucata](<yucata_url>)",
        "boite": "[<name> on Boite a Jeux](<boite_url>)",
    }
    """
    game = Game(game_name.lower())
    if debug:
        print(f'SEARCHING WEB FOR GAME DATA: {game.name}')
    game_on_bgg = get_bgg_data(game, debug)
    if not game_on_bgg:
        possible_game = get_non_exact_bgg_data(game, debug)
        if possible_game:
            return search_web_board_game_data(possible_game)
    if game_on_bgg:
        get_bga_data(game, debug)
        get_boite_a_jeux_data(game, debug)
        get_tabletopia_data(game, debug)
        get_tts_data(game, debug)
        get_yucata_data(game, debug)
        game_data = game.return_game_data()
        if debug:
            print(f'GAME DATA FOUND:\n{game_data}')
        return game_data
    return False

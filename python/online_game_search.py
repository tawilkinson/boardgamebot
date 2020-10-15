import lxml
import json
import html
import requests
import time
import difflib
from bs4 import BeautifulSoup


class Webpage(BeautifulSoup):
    def __init__(self, url):
        self.response = requests.get(url)
        self.page_response = self.response
        self.page_html = BeautifulSoup(self.response.text, 'lxml')

class Game:
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
        self.tts_search_url = f'https://steamcommunity.com/workshop/browse/?appid=286160&searchtext={self.name}&browsesort=textsearch&section=readytouseitems&requiredtags%5B0%5D=Game&actualsort=textsearch&p=1'
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
    if debug:
        print(f'> Boite a Jeux: {game.boite_search_url}')
    boite_directory_page = Webpage(game.boite_search_url).page_html
    search_results = boite_directory_page.find_all('div', class_='jeuxRegles')
    for res in search_results:
        if game.name.lower() in res.text.lower():
            rules_elem = res.select_one('a', text='Rules')
            rules_href = rules_elem.get('href')
            game_boite_url = f'http://www.boiteajeux.net/{rules_href}'
            game.set_boite_url(f'[{game.name} on BGA]({game_boite_url}')


def get_bgg_data(game, debug=False):
    if debug:
        print(f'> Board Game Geek: {game.bgg_search_url}')
    bgg_search = Webpage(game.bgg_search_url)
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
        bgg_page = Webpage(bbg_url)
        game_description = html.unescape(
            bgg_page.page_html.items.description.text)
        abridged_game_description = f'{game_description[0:300]} ...'
        game.set_description(abridged_game_description)
        game_image = bgg_page.page_html.items.image.text
        game.set_image(game_image)
        if debug:
            print(f'--> retrieved {game.name} Board Game Geek data')
        return True

def get_non_exact_bgg_data(game, debug=False):
    if debug:
        print(f'> Board Game Geek: {game.bgg_non_exact_search_url}')
    bgg_search = Webpage(game.bgg_non_exact_search_url)
    games_found = bgg_search.page_html.items['total']

    if games_found == '0':
        game.set_description(
            'Game not found on Board Game Geek! Is it even a board game?')
        if debug:
            print(f'> !!! No potential matches for {game.name} found on Board Game Geek !!!')
        return False

    else:
        board_game_search = bgg_search.page_html.items.findAll('item')
        possible_board_games = [game_search.find('name').get('value') for game_search in board_game_search]
        if debug:
            print(f'--> found {len(possible_board_games)} potential matches on Board Game Geek')
        closest_match = difflib.get_close_matches(game.name, possible_board_games, 1)[0]
        if debug:
            print(f'--> {closest_match} is closest match')
        return closest_match

def get_tabletopia_data(game, debug=False):
    if debug:
        print(f'> Tabletopia: {game.tabletopia_search_url}')
    tabletopia_games = []
    tabletopia_directory_page = Webpage(game.tabletopia_search_url).page_html
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


def get_tts_data(game, debug=False):
    if debug:
        print(f'> Tabletop Simulator: {game.tts_search_url}')
    tts_dlc_search = Webpage(game.tts_dlc_url).page_html
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
                print(f'--> retrieved {game.name} Tabletop Simulator DLC data')
            break
    tts_search = Webpage(game.tts_search_url).page_html
    search_results = tts_search.body.select('body a')
    for result in search_results:
        url = result['href']
        if 'https://steamcommunity.com' in url:
            url = url.replace(
                '/url?q=',
                '').replace(
                '%3F',
                '?').replace(
                '%3D',
                '=').split('&')[0]
            game.set_tts_url(f"{dlc}[ {game.name} on Steam Workshop]({url})")
            if debug:
                print(
                    f'--> retrieved {game.name} Tabletop Simulator Steam Workshop data')
            break


def get_bga_data(game, debug=False):
    if debug:
        print(f'> Board Game Arena: {game.bga_search_url}')
    bga_page = Webpage(game.bga_search_url).page_html.body
    bga_page_text = bga_page.text
    if 'Sorry, an unexpected error has occurred...' not in bga_page_text:
        game.set_bga_url(f'[{game.name} on BGA]({game.bga_search_url})')
        if debug:
            print(f'--> retrieved {game.name} Board Game Arena data')


def get_yucata_data(game, debug=False):
    if debug:
        print(f'> Yucata: {game.yucata_search_url}')
    yucata_games = []
    yucata_directory_page = Webpage(game.yucata_search_url).page_html
    search_results = yucata_directory_page.find_all('a', class_='jGameInfo')
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


def search_web_board_game_data(game_name, debug=True):
    game = Game(game_name)
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

import lxml
import json
import html
import requests
import time
from bs4 import BeautifulSoup

class Webpage(BeautifulSoup):
    def __init__(self, url):
        self.response=requests.get(url)
        self.page_response=self.response
        self.page_html=BeautifulSoup(self.response.text, 'lxml')

class Game:
    def __init__(self, name):
        self.name=name.title()
        self.search_name=self.name.lower().strip()
        self.app=''
        self.bga=False
        self.bga_search_url=f'https://boardgamearena.com/gamepanel?game={self.search_name}'
        self.bgg=''
        self.bgg_search_url=f'http://www.boardgamegeek.com/xmlapi2/search?query={self.search_name}&exact=1&type=boardgame'
        self.boite=False
        self.description=False
        self.image=''
        self.tabletopia=''
        self.tabletopia_search_url=f'https://tabletopia.com/playground/playgroundsearch/search?timestamp={int(time.time() * 1000)}&query={self.name}' #.replace(' ','%20')
        self.tts=False
        self.tts_search_url=f'https://www.google.com/search?q=tabletop+simulator+{self.name}&num=1'
        self.yucata=False

    def set_description(self, description):
        self.description=description

    def set_image(self, description):
        self.image=description

    def set_bga_url(self, url):
        self.bga=url

    def set_boite_url(self, url):
        self.boite=url

    def set_tabletopia_url(self, url):
        self.tabletopia=url

    def set_tts_url(self, tts):
        self.tts=tts

    def set_yucata_url(self, url):
        self.yucata=url

    def get_set_bgg_url(self, id):
        self.bgg=f'https://boardgamegeek.com/boardgame/{id}/'
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
        print('http://www.boiteajeux.net/index.php?p=regles')
    boite_directory_page = Webpage('http://www.boiteajeux.net/index.php?p=regles').page_html
    search_results = boite_directory_page.find_all('div', class_='jeuxRegles')
    for res in search_results:
        if game.name.lower() in res.text.lower():
            rules_elem = res.select_one('a', text='Rules')
            rules_href = rules_elem.get('href')
            game_boite_url=f'http://www.boiteajeux.net/{rules_href}'
            if debug:
                print(game_boite_url)
            game.set_boite_url(f'[{game.name} on BGA]({game_boite_url}')


def get_bgg_data(game, debug=False):
    bgg_search = Webpage(game.bgg_search_url)
    games_found = bgg_search.page_html.items['total']

    if games_found == '0':
        game.set_description('Game not found on Board Game Geek! Is it even a board game?')
        if debug:
            print(f'No games with that name found on BBG.\n > query:{game.bgg_search_url}')
        return False

    else:
        id = bgg_search.page_html.items.item['id']
        bbg_url = game.get_set_bgg_url(id)
        bgg_page = Webpage(bbg_url)
        game_description = html.unescape(bgg_page.page_html.items.description.text)
        abridged_game_description = f'{game_description[0:300]} ...'
        game.set_description(abridged_game_description)
        game_image = bgg_page.page_html.items.image.text
        game.set_image(game_image)

        if debug:
            print(f'> query:{bbg_url}')
            print(abridged_game_description)
        return True


def get_tabletopia_data(game, debug=False):
    tabletopia_games = []
    if debug:
        print(game.tabletopia_search_url)
    tabletopia_directory_page = Webpage(game.tabletopia_search_url).page_html
    search_results = tabletopia_directory_page.find_all('a', class_='dropdown-menu__item dropdown-item-thumb')
    for result in search_results:
        if debug:
            print(result)
        game_name = result.text.strip()
        game_tabletopia_url = result['href']
        game_tabletopia_url = f'https://tabletopia.com{game_tabletopia_url}'
        formatted_link = f'[{game_name} on Tabletopia]({game_tabletopia_url})'
        tabletopia_games.append(formatted_link)
    if tabletopia_games:
        game.set_tabletopia_url('\n'.join(tabletopia_games))


def get_tts_data(game, debug=False):
    if debug:
        print(game.tts_search_url)
    tts_search = Webpage(game.tts_search_url).page_html
    search_results = tts_search.body.select('body a')
    for result in search_results:
        url = result['href']
        if 'https://steamcommunity.com' in url:
            url = url.replace('/url?q=','').replace('%3F','?').replace('%3D','=').split('&')[0]
            if debug:
                print('https://steamcommunity.com/sharedfiles/filedetails/?id=263788054')
            game.set_tts_url(f"[Steam Workshop]({url})")
            break


def get_bga_data(game, debug=False):
    if debug:
        print(game.bga_search_url)
    bga_page = Webpage(game.bga_search_url).page_html.body
    bga_page_text = bga_page.text
    if 'Game not found' not in bga_page_text:
        game.set_bga_url(f'[{game.name} on BGA]({game.bga_search_url})')


def get_yucata_data(game, debug=False):
    yucata_games = []
    if debug:
        print('https://www.yucata.de/en/')
    boite_directory_page = Webpage('https://www.yucata.de/en/').page_html
    search_results = boite_directory_page.find_all('a', class_='jGameInfo')
    for res in search_results:
        if game.name.lower() in res.text.lower():
            game_href = res['href']
            game_name = res.text
            game_yucata_url = f'https://www.yucata.de{game_href}'
            formatted_link = f'[{game_name} on Yucata]({game_yucata_url})'
            yucata_games.append(formatted_link)
    if yucata_games:
        game.set_yucata_url('\n'.join(yucata_games))


def search_web_board_game_data(game_name, debug=False):
    game = Game(game_name)
    if debug:
        print(f'Searching for {game.name}')
    game_on_bgg = get_bgg_data(game, debug)
    if game_on_bgg:
        get_bga_data(game)
        get_boite_a_jeux_data(game)
        get_tabletopia_data(game)
        get_tts_data(game)
        get_yucata_data(game)
    game_data = game.return_game_data()
    if debug:
        print(game_data)
    return game_data

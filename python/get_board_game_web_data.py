"""
This script will iterate over a list of board games (human name) and search for
information on these games on BGG and other board game websites.
"""
import lxml
import json
import requests
from bs4 import BeautifulSoup

DEBUG=False
LIST_OF_GAMES_INFO=dict(games=[])

class Webpage(BeautifulSoup):
    def __init__(self, url):
        self.response=requests.get(url)
        self.page_response=self.response
        self.page_html=BeautifulSoup(self.response.text, 'lxml')

class Game:
    def __init__(self, name):
        self.name=name
        self.app=''
        self.bga='false'
        self.bga_search_url=f'https://boardgamearena.com/gamepanel?game={self.name.strip()}'
        self.bgg_id=''
        self.bgg=''
        self.bgg_search_url=f'http://www.boardgamegeek.com/xmlapi2/search?query={self.name}&exact=1&type=boardgame'
        self.boite='false'
        self.description=''
        self.image=''
        self.tabletopia=''
        self.tts='false'
        self.tts_search_url=f'https://www.google.com/search?q=tabletop+simulator+{self.name}&num=1'
        self.yucata='false'

    def set_description(self, description):
        self.description=description

    def set_bga_url(self, url):
        self.bga=url

    def set_boite_url(self, url):
        self.boite=url

    def set_tts_url(self, tts):
        self.tts=tts

    def set_yucata_url(self, url):
        self.yucata=url

    def get_set_bgg_url(self):
        self.bgg=f'https://boardgamegeek.com/boardgame/{self.bgg_id}/'
        return f'http://www.boardgamegeek.com/xmlapi2/thing?id={self.bgg_id}'

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
        game.set_description('Game not found')
        if DEBUG:
            print(f'No games with that name found on BBG.\n > query:{game.bgg_search_url}')

    else:
        game.bgg_id = bgg_search.page_html.items.item['id']
        bbg_url = game.get_set_bgg_url()
        if DEBUG:
            print(f'BGG game id found={game.bgg_id}')

        bgg_page = Webpage(bbg_url)
        game_description = bgg_page.page_html.items.description.text
        game.set_description(game_description)
        if DEBUG:
            print(f'> query:{bbg_url}')
            print(bgg_page.page_html.items.description.text)


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
            formatted_link = f'[{game_name} on Yucata]({game_yucata_url}'
            yucata_games.append(formatted_link)
    if yucata_games:
        game.set_yucata_url('\n'.join(yucata_games))


def main():

    with open('./bot/data/game_list.txt') as input:
        game_names=[line.strip() for line in input]

    for game_name in game_names:
        game = Game(game_name)

        if DEBUG:
            print(f'Searching for {game.name}')

        # BOARD GAME GEEK SEARCH
        get_bgg_data(game)

        # BOARD GAME ARENA SEARCH
        get_bga_data(game)

        # BOITE A JEUX SEARCH
        get_boite_a_jeux_data(game)

        # TABLETOP SIMULATOR SEARCH
        get_tts_data(game)

        # YUCATA SEARCH
        get_yucata_data(game)

        # PRINT OUT GAME DATA
        game_data_output = game.return_game_data()

        LIST_OF_GAMES_INFO['games'].append(game_data_output)

    with open('./bot/data/games_test.json','w+') as output:
        output.write(json.dumps(LIST_OF_GAMES_INFO))


if __name__ == '__main__':
    main()

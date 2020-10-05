"""
This script will iterate over a list of board games (human name) and secrach for
information on these games on BGG and other board game websites.
"""
import lxml
import requests
from bs4 import BeautifulSoup

DEBUG=False
LIST_OF_GAMES_INFO=dict(games=[])

class Webpage(BeautifulSoup):
    def __init__(self, url):
        self.response=requests.get(url)
        self.page_html=BeautifulSoup(self.response.text, 'lxml')

class Game:
    def __init__(self, name):
        self.name=name
        self.bgg_id=''
        self.bgg_search_url=f'http://www.boardgamegeek.com/xmlapi2/search?query={self.name}&exact=1&type=boardgame'
        self.description=''
        self.bgg=''
        self.image=''
        self.tabletopia=''
        self.tts='false'
        self.tts_search_url=f'https://www.google.com/search?q=tabletop+simulator+{self.name}&num=1'
        self.bga=''
        self.yucata=''
        self.boite=''
        self.app=''

    def set_description(self, description):
        self.description=description

    def set_tts_details(self, tts):
        self.tts=tts

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
            game.set_tts_details(f"[Steam Workshop]({url})")
            break

def main():
    game_names = ["Carcassonne"]
    for game_name in game_names:
        game = Game(game_name)

        if DEBUG:
            print(f'Searching for {game.name}')

        # BOARD GAME GEEK SEARCH
        get_bgg_data(game)

        # TABLETOP SIMULATOR SEARCH
        get_tts_data(game)

        # PRINT OUT GAME DATA
        game_data_output = game.return_game_data()
        if DEBUG:
            print(game_data_output)

    LIST_OF_GAMES_INFO['games'].append(game_data_output)
    print(LIST_OF_GAMES_INFO)

if __name__ == '__main__':
    main()

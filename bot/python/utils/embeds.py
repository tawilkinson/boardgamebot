import discord
import logging
import time
from utils.colour import get_discord_colour
from utils.helpers import Site

logger = logging.getLogger('discord')


class GameEmbed():
    '''Board game search functions.'''

    def __init__(self, game=None, site=0):
        self.cont = 1
        self.embed = None
        self.embeds = []
        self.game = game
        self.site = site

    def base_game_embed(self):
        if self.cont > 1:
            title = self.game['name'] + f' ({self.cont})'
            description = 'More game links below'
        else:
            title = self.game['name']
            description = self.game['description'][:2047]

        colour = get_discord_colour(self.game['image'])
        self.embed = discord.Embed(
            title=title, description=description, colour=colour)
        self.embed.set_thumbnail(url=self.game['image'])
        if self.cont == 1:
            bgg_text = '[' + self.game['name'] + '](' + self.game['bgg'] + ')'
            self.embed.add_field(name='Read more at BGG',
                                 value=bgg_text, inline=False)

    def base_site_embed(self):
        if Site(self.site) == Site.bga:
            title_str = 'Board Game Arena Games'
            description = 'Join the largest boardgame table in the world.\
                \nNo download necessary - play directly from your web browser.\
                \nWith your friends and thousands of players from the whole world.\
                \nFree.'
            url = 'https://boardgamearena.com/gamelist'
            colour = 0x9566DD
            thumb_url = 'https://x.boardgamearena.net/data/themereleases/200316-1631/img/logo/logo.png'
        elif Site(self.site) == Site.boite:
            title_str = 'Boîte à Jeux Games'
            description = 'Boîte à Jeux is a predominantly French online game system. The \
                interface has been translated to English and more recently, German as well.\
                \nGames are played in a web browser one turn at a time, which could take hours \
                or weeks, depending on the game and how often the players take their turns. \
                    Live games are possible if players are both logged in at the same time.'
            url = 'http://www.boiteajeux.net/'
            colour = 0x55774C
            thumb_url = 'http://www.boiteajeux.net/img/banniere_baj_en.png'
        elif Site(self.site) == Site.yucata:
            title_str = 'Yucata.de Games'
            description = 'Online gaming portal, free and without advertisements \
                where you may play more than 60 different games.'
            url = 'https://www.yucata.de/en'
            colour = 0x00305E
            thumb_url = 'https://www.yucata.de/bundles/images/Logo.jpg'
        elif Site(self.site) == Site.tts:
            title_str = 'Tabletop Simulator DLC'
            description = 'Tabletop Simulator is the only simulator \
                where you can let your aggression out by flipping the \
                table! There are no rules to follow: just you, a physics \
                sandbox, and your friends. Make your own online board \
                games or play the thousands of community created mods. \
                Unlimited gaming possibilities!'
            url = 'https://store.steampowered.com/search/?term=tabletop+simulator&category1=21'
            colour = 0xE86932
            thumb_url = 'https://cdn.akamai.steamstatic.com/steam/apps/286160/header.jpg'
        else:
            self.embed = discord.Embed()
            return
        if self.cont > 1:
            title = f'{title_str} ({self.cont})'
            description = 'More game links below'
        else:
            title = f'{title_str}'

        self.embed = discord.Embed(
            title=title, description=description, colour=colour, url=url)
        self.embed.set_thumbnail(url=thumb_url)

    def embed_constrain(self, name, value):
        self.embeds.append(self.embed)
        if self.game:
            self.base_game_embed()
        else:
            self.base_site_embed()
        self.embed.add_field(name=name, value=value)

    def link_constrain(self, all_links, site=''):
        count = 1
        value = ''
        for text in all_links:
            name = f'{site} ' + str(count) + ':'
            field_len = len(value) + len(text) + len(name)
            embed_len = field_len + len(self.embed)
            if (field_len) > 1022 or (embed_len > 5999):
                count += 1
                self.cont += 1
                if (len(value) + len(self.embed) > 5999):
                    value = value.replace('\n', '; ')
                    self.embed_constrain(name, value)
                value = ''
            else:
                value += text
                value += '\n'
        return value, name

    def format_game_embed(self, full_time=None):
        self.cont = 1
        self.embeds = []
        self.base_game_embed()

        # Board Game Arena field
        if not self.game['bga']:
            self.embed.add_field(name='Board Game Arena', value='❌')
        else:
            link = self.game['bga']
            self.embed.add_field(name='Board Game Arena', value=link)

        # Boîte à Jeux field
        if not self.game['boite']:
            self.embed.add_field(name='Boîte à Jeux', value='❌')
        else:
            link = self.game['boite']
            self.embed.add_field(name='Boîte à Jeux', value=link)

        # Yucata field
        if not self.game['yucata']:
            self.embed.add_field(name='Yucata', value='❌')
        else:
            link = self.game['yucata']
            self.embed.add_field(name='Yucata', value=link)

        # Tabletopia field
        if not self.game['tabletopia']:
            self.embed.add_field(name='Tabletopia', value='❌')
        else:
            link = self.game['tabletopia']
            if len(link) > 1022:
                all_links = link.split('\n')
                self.link_constrain(self, all_links, site='Tabletopia')
            else:
                link = link.rstrip('\n').replace('\n', '; ')
                self.embed.add_field(name='Tabletopia', value=link)

        # Tabletop Simulator field
        if not self.game['tts']:
            self.embed.add_field(name='Tabletop Simulator', value='❌')
        else:
            link = self.game['tts']
            if len(link) > 1022:
                all_links = link.split('\n')
                value, name = self.link_constrain(
                    self, all_links, site='Tabletop Simulator')
                if value:
                    self.cont += 1
                    value = value.replace('\n', '; ')
                    self.embed_constrain(name, value)
            else:
                link = link.rstrip('\n').replace('\n', '; ')
                self.embed.add_field(name='Tabletop Simulator', value=link)

        self.embeds.append(self.embed)

        count = 1
        for emb in self.embeds:
            footer_txt = ''
            if len(self.embeds) > 1:
                footer_txt += f'({count}/{len(self.embeds)}) '
                count += 1
            if full_time:
                footer_txt += f'Fetched in {full_time:0.2f}s'
            emb.set_footer(text=footer_txt)

        return self.embeds

    def format_all_games_embed(self, all_links, start_time=None):
        self.cont = 1
        self.embeds = []
        self.base_site_embed()
        count = 1
        alphabet = None
        value = ''
        for link, text in sorted(all_links.items()):
            name = link[0]
            if alphabet is None:
                alphabet = name
            embed_len = len(alphabet) + len(value) + \
                len(self.embed) + len(name)
            field_len = len(alphabet) + len(value) + len(text) + len(name)
            if name != alphabet[0]:
                if embed_len > 5998:
                    count += 1
                    self.cont += 1
                    self.embed_constrain(alphabet, value)
                else:
                    self.embed.add_field(name=alphabet, value=value)
                alphabet = name
                value = text
            else:
                if embed_len > 5998:
                    count += 1
                    self.cont += 1
                    self.embed_constrain(alphabet, value)
                    alphabet = f'{name} (cont...)'
                    value = text
                elif field_len > 1022:
                    self.embed.add_field(name=alphabet, value=value)
                    alphabet = f'{name} (cont...)'
                    value = text
                else:
                    if value:
                        value += f'; {text}'
                    else:
                        value = text
        self.embeds.append(self.embed)
        if start_time:
            full_time = time.time() - start_time
        for emb in self.embeds:
            count = 1
            footer_txt = ''
            if len(self.embeds) > 1:
                footer_txt += f'({count}/{len(self.embeds)}) '
                count += 1
            if start_time:
                footer_txt += f'Fetched in {full_time:0.2f}s'
            emb.set_footer(text=footer_txt)

        return self.embeds

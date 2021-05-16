import discord
import logging
import time
from utils.colour import get_discord_colour
from utils.helpers import Site
from utils.online_game_search import get_all_games

logger = logging.getLogger('discord')


class GameEmbed():
    '''Board game search functions.'''

    def __init__(self):
        self.cont = 1

    def base_game_embed(self, game):
        if self.cont > 1:
            title = game['name'] + f' ({self.cont})'
            description = 'More game links below'
        else:
            title = game['name']
            description = game['description'][:2047]

        colour = get_discord_colour(game['image'])
        embed = discord.Embed(
            title=title, description=description, colour=colour)
        embed.set_thumbnail(url=game['image'])
        if self.cont == 1:
            bgg_text = '[' + game['name'] + '](' + game['bgg'] + ')'
            embed.add_field(name='Read more at BGG',
                            value=bgg_text, inline=False)
        return embed

    def base_site_embed(self, site=0):
        if Site(site) == Site.bga:
            title_str = 'Board Game Arena Games'
            description = 'Join the largest boardgame table in the world.\
                \nNo download necessary - play directly from your web browser.\
                \nWith your friends and thousands of players from the whole world.\
                \nFree.'
            url = 'https://boardgamearena.com/gamelist'
            colour = 0x9566DD
            thumb_url = 'https://x.boardgamearena.net/data/themereleases/200316-1631/img/logo/logo.png'
        elif Site(site) == Site.boite:
            title_str = 'Boîte à Jeux Games'
            description = 'Boîte à Jeux is a predominantly French online game system. The \
                interface has been translated to English and more recently, German as well.\
                \nGames are played in a web browser one turn at a time, which could take hours \
                or weeks, depending on the game and how often the players take their turns. \
                    Live games are possible if players are both logged in at the same time.'
            url = 'http://www.boiteajeux.net/'
            colour = 0x55774C
            thumb_url = 'http://www.boiteajeux.net/img/banniere_baj_en.png'
        elif Site(site) == Site.yucata:
            title_str = 'Yucata.de Games'
            description = 'Online gaming portal, free and without advertisements \
                where you may play more than 60 different games.'
            url = 'https://www.yucata.de/en'
            colour = 0x00305E
            thumb_url = 'https://www.yucata.de/bundles/images/Logo.jpg'
        elif Site(site) == Site.tts:
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
            embed = discord.Embed()
            return embed
        if self.cont > 1:
            title = f'{title_str} ({self.cont})'
            description = 'More game links below'
        else:
            title = f'{title_str}'

        embed = discord.Embed(
            title=title, description=description, colour=colour, url=url)
        embed.set_thumbnail(url=thumb_url)
        return embed

    def embed_constrain(self, name, value, embed, embeds, site=0, game=None, ):
        embeds.append(embed)
        if game:
            embed = self.base_game_embed(game)
        else:
            embed = self.base_site_embed(site)
        embed.add_field(name=name, value=value)
        return embed, embeds

    def format_game_embed(self, game, full_time=None):
        self.cont = 1
        embeds = []
        embed = self.base_game_embed(game)

        # Board Game Arena field
        if not game['bga']:
            embed.add_field(name='Board Game Arena', value='❌')
        else:
            link = game['bga']
            embed.add_field(name='Board Game Arena', value=link)

        # Boîte à Jeux field
        if not game['boite']:
            embed.add_field(name='Boîte à Jeux', value='❌')
        else:
            link = game['boite']
            embed.add_field(name='Boîte à Jeux', value=link)

        # Yucata field
        if not game['yucata']:
            embed.add_field(name='Yucata', value='❌')
        else:
            link = game['yucata']
            embed.add_field(name='Yucata', value=link)

        # Tabletopia field
        if not game['tabletopia']:
            embed.add_field(name='Tabletopia', value='❌')
        else:
            link = game['tabletopia']
            if len(link) > 1022:
                all_links = link.split('\n')
                count = 1
                value = ''
                for text in all_links:
                    name = 'Tabletopia ' + str(count) + ':'
                    field_len = len(value) + len(text) + len(name)
                    embed_len = field_len + len(embed)
                    if (field_len) > 1022 or (embed_len > 5999):
                        count += 1
                        self.cont += 1
                        if (len(value) + len(embed) > 5999):
                            value = value.replace('\n', '; ')
                            embed, embeds = self.embed_constrain(
                                name, value, embed, embeds, game=game)
                        value = ''
                    else:
                        value += text
                        value += '\n'
            else:
                link = link.rstrip('\n').replace('\n', '; ')
                embed.add_field(name='Tabletopia', value=link)

        # Tabletop Simulator field
        if not game['tts']:
            embed.add_field(name='Tabletop Simulator', value='❌')
        else:
            link = game['tts']
            if len(link) > 1022:
                all_links = link.split('\n')
                count = 1
                value = ''
                for text in all_links:
                    name = 'Tabletop Simulator ' + str(count) + ':'
                    field_len = len(value) + len(text) + len(name)
                    embed_len = field_len + len(embed)
                    if (field_len) > 1022 or (embed_len > 5999):
                        self.cont += 1
                        value = value.replace('\n', '; ')
                        embed, embeds = self.embed_constrain(
                            name, value, embed, embeds, game)
                        count += 1
                        value = ''
                    else:
                        value += text
                        value += '\n'
                if value:
                    self.cont += 1
                    value = value.replace('\n', '; ')
                    embed, embeds = self.embed_constrain(name, value,
                                                         embed, embeds, game)
            else:
                link = link.rstrip('\n').replace('\n', '; ')
                embed.add_field(name='Tabletop Simulator', value=link)

        embeds.append(embed)

        count = 1
        for emb in embeds:
            footer_txt = ''
            if len(embeds) > 1:
                footer_txt += f'({count}/{len(embeds)}) '
                count += 1
            if full_time:
                footer_txt += f'Fetched in {full_time:0.2f}s'
            emb.set_footer(text=footer_txt)

        return embeds

    def format_all_games_embed(self, all_links, site=0, start_time=None):
        self.cont = 1
        embeds = []
        embed = self.base_site_embed(site)
        count = 1
        alphabet = None
        value = ''
        for link, text in sorted(all_links.items()):
            name = link[0]
            if alphabet is None:
                alphabet = name
            embed_len = len(alphabet) + len(value) + len(embed) + len(name)
            field_len = len(alphabet) + len(value) + len(text) + len(name)
            if name != alphabet[0]:
                if embed_len > 5998:
                    count += 1
                    self.cont += 1
                    embed, embeds = self.embed_constrain(
                        alphabet, value, embed, embeds, site)
                else:
                    embed.add_field(name=alphabet, value=value)
                alphabet = name
                value = text
            else:
                if embed_len > 5998:
                    count += 1
                    self.cont += 1
                    embed, embeds = self.embed_constrain(
                        alphabet, value, embed, embeds, site)
                    alphabet = f'{name} (cont...)'
                    value = text
                elif field_len > 1022:
                    embed.add_field(name=alphabet, value=value)
                    alphabet = f'{name} (cont...)'
                    value = text
                else:
                    if value:
                        value += f'; {text}'
                    else:
                        value = text
        embeds.append(embed)
        if start_time:
            full_time = time.time() - start_time
        for emb in embeds:
            count = 1
            footer_txt = ''
            if len(embeds) > 1:
                footer_txt += f'({count}/{len(embeds)}) '
                count += 1
            if start_time:
                footer_txt += f'Fetched in {full_time:0.2f}s'
            emb.set_footer(text=footer_txt)

        return embeds

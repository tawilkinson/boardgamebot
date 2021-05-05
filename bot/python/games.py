import discord
import DiscordUtils
import logging
import re
import string
from discord.ext import commands
from colour import get_discord_colour
from online_game_search import search_web_board_game_data, get_all_games

logger = logging.getLogger('discord')


class Games(commands.Cog, name='games'):
    '''Board game search functions.'''

    def __init__(self, bot):
        self.bot = bot
        self.cont = 1
        self.end_regex = r'\s\([0-9]+\)$'
        self.parser = re.compile(self.end_regex)

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

    def base_site_embed(self, bga=None, boite=None, yucata=None, tts=None):
        title_str = ''
        if bga:
            title_str = 'Board Game Arena Games'
            description = 'Join the largest boardgame table in the world.\
                \nNo download necessary - play directly from your web browser.\
                \nWith your friends and thousands of players from the whole world.\
                \nFree.'
            url = 'https://boardgamearena.com/gamelist'
            colour = 0x9566DD
            thumb_url = 'https://x.boardgamearena.net/data/themereleases/200316-1631/img/logo/logo.png'
        if boite:
            title_str = 'Boîte à Jeux Games'
            description = 'Boîte à Jeux is a predominantly French online game system. The \
                interface has been translated to English and more recently, German as well.\
                \nGames are played in a web browser one turn at a time, which could take hours \
                or weeks, depending on the game and how often the players take their turns. \
                    Live games are possible if players are both logged in at the same time.'
            url = 'http://www.boiteajeux.net/'
            colour = 0x55774C
            thumb_url = 'http://www.boiteajeux.net/img/banniere_baj_en.png'
        if yucata:
            title_str = 'Yucata.de Games'
            description = 'Online gaming portal, free and without advertisements \
                where you may play more than 60 different games.'
            url = 'https://www.yucata.de/en'
            colour = 0x00305E
            thumb_url = 'https://www.yucata.de/bundles/images/Logo.jpg'
        if tts:
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
        if self.cont > 1:
            title = f'{title_str} ({self.cont})'
            description = 'More game links below'
        else:
            title = f'{title_str}'

        embed = discord.Embed(
            title=title, description=description, colour=colour, url=url)
        embed.set_thumbnail(url=thumb_url)
        return embed

    def embed_constrain(self, name, value, embed, embeds, game=None, bga=None,
                        boite=None, yucata=None, tts=None):
        embeds.append(embed)
        if game:
            embed = self.base_game_embed(game)
        else:
            embed = self.base_site_embed(
                bga=bga, boite=boite, tts=tts, yucata=yucata)
        embed.add_field(name=name, value=value)
        return embed, embeds

    def format_game_embed(self, game):
        self.cont = 1
        embeds = []
        embed = self.base_game_embed(game)

        # App field, needs fixing
        # if not game['app']:
        #     embed.add_field(name='App:', value='❌')
        # else:
        #    link = game['app']
        #    embed.add_field(name='App:', value=link)

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

        return embeds

    def format_all_games_embed(
            self,
            bga=False,
            boite=False,
            tts=False,
            yucata=False):
        self.cont = 1
        embeds = []
        embed = self.base_site_embed(
            bga=bga, boite=boite, tts=tts, yucata=yucata)
        all_links = get_all_games(bga, boite, tts, yucata)
        if all_links is None:
            return embeds
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
                        alphabet, value, embed, embeds, bga=bga, boite=boite, tts=tts, yucata=yucata)
                else:
                    embed.add_field(name=alphabet, value=value)
                alphabet = name
                value = text
            else:
                if embed_len > 5998:
                    count += 1
                    self.cont += 1
                    embed, embeds = self.embed_constrain(
                        alphabet, value, embed, embeds, bga=bga, boite=boite, tts=tts, yucata=yucata)
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

        return embeds

    @commands.command(aliases=['g', 'search', 's', 'boardgame', 'bg'],
                      help='Print detailed info about a board game. \
                          Fetches game info from [BGG](https://boardgamegeek.com/) \
                              then returns online sources, if they exist, to play \
                                  the game.')
    async def game(self, ctx, *game):
        game_str = ' '.join(game)
        game_str = string.capwords(game_str)
        if game_str is None:
            response = f'Please enter a game to search: `bg game <game_name>`. '
            await ctx.send(response)
        else:
            response = 'Searching for ' + game_str + ', standby whilst I search online...'
            message = await ctx.send(response)
            search_game = await search_web_board_game_data(
                game_str, message, ctx)
            if search_game:
                responses = self.format_game_embed(search_game)
                if len(responses) > 1:
                    paginator = DiscordUtils.Pagination.AutoEmbedPaginator(
                        ctx, timeout=60, auto_footer=True)
                    await paginator.run(responses)
                else:
                    await ctx.send(content='', embed=responses[0])
                await message.delete()

            else:
                response = game_str + ' not found online.'
                await message.edit(content=response)

    @commands.command(aliases=['board_game_arena', 'boardgamearena'],
                      help='Prints the list of games currently available on Board Game Arena.')
    async def bga(self, ctx):
        response = 'Getting the list of BGA games...'
        message = await ctx.send(response)
        responses = self.format_all_games_embed(bga=True)
        await message.delete()
        if len(responses) > 1:
            paginator = DiscordUtils.Pagination.AutoEmbedPaginator(
                ctx, timeout=60, auto_footer=True)
            await paginator.run(responses)
        else:
            await ctx.send(content='', embed=responses[0])

    @commands.command(
        aliases=[
            'boite_a_jeux',
            'boiteajeux',
            'boîte',
            'boîte_à_jeux',
            'boîteàjeux'],
        help='Prints the list of games currently available on Boîte à Jeux.')
    async def boite(self, ctx):
        response = 'Getting the list of Boîte à Jeux games...'
        message = await ctx.send(response)
        responses = self.format_all_games_embed(boite=True)
        await message.delete()
        if len(responses) > 1:
            paginator = DiscordUtils.Pagination.AutoEmbedPaginator(
                ctx, timeout=60, auto_footer=True)
            await paginator.run(responses)
        else:
            await ctx.send(content='', embed=responses[0])

    @commands.command(help='Tabletopia has over 1600 games, so prints a link to the all games page on Tabletopia.')
    async def tabletopia(self, ctx):
        description = 'Tabletopia has over 1600 games. Full list at [Tabletopia: All Games](https://tabletopia.com/games?page=1).'
        embed = discord.Embed(
            title='Tabletopia Games',
            description=description,
            colour=0xFD9705,
            url='https://tabletopia.com/games?page=1')
        embed.set_thumbnail(
            url='https://tabletopia.com/Content/Images/logo.png')
        await ctx.send(embed=embed)

    @commands.command(aliases=['tabletop_simulator', 'tabletopsimulator'],
                      help='Prints the list of DLC currently available for Tabletop Simulator.')
    async def tts(self, ctx):
        response = 'Getting the list of Tabletop Simulator DLC...'
        message = await ctx.send(response)
        responses = self.format_all_games_embed(tts=True)
        await message.delete()
        if len(responses) > 1:
            paginator = DiscordUtils.Pagination.AutoEmbedPaginator(
                ctx, timeout=60, auto_footer=True)
            await paginator.run(responses)
        else:
            await ctx.send(content='', embed=responses[0])

    @commands.command(aliases=['yucata.de'],
                      help='Prints the list of games currently available on Yucata.de.')
    async def yucata(self, ctx):
        response = 'Getting the list of Yucata games...'
        message = await ctx.send(response)
        responses = self.format_all_games_embed(yucata=True)
        await message.delete()
        if len(responses) > 1:
            paginator = DiscordUtils.Pagination.AutoEmbedPaginator(
                ctx, timeout=60, auto_footer=True)
            await paginator.run(responses)
        else:
            await ctx.send(content='', embed=responses[0])

    @commands.command(help='Lists the help for command category `games`.',
                      pass_context=True)
    async def games(self, ctx):
        await ctx.invoke(self.bot.get_command('help'), 'games')


def setup(bot):
    bot.add_cog(Games(bot))

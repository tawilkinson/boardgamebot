import discord
import re
import string
from discord.ext import commands
from colour import get_discord_colour
from online_game_search import search_web_board_game_data, get_all_games


class Games(commands.Cog, name='games'):
    '''Board game search functions.'''

    def __init__(self, bot):
        self.bot = bot
        self.cont = 1
        self.end_regex = r'\s\([0-9]+\)$'
        self.parser = re.compile(self.end_regex)

    def base_embed(self, game):
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

    def base_bga_embed(self):
        if self.cont > 1:
            title = f'Board Game Arena Games ({self.cont})'
            description = 'More game links below'
        else:
            title = f'Board Game Arena Games'
            description = 'Join the largest boardgame table in the world.\
                \nNo download necessary - play directly from your web browser.\
                \nWith your friends and thousands of players from the whole world.\
                \nFree.'
        url = 'https://boardgamearena.com/gamelist'
        colour = 0x9566DD
        embed = discord.Embed(
            title=title, description=description, colour=colour, url=url)
        embed.set_thumbnail(
            url='https://x.boardgamearena.net/data/themereleases/200316-1631/img/logo/logo.png')
        return embed

    def base_yucata_embed(self):
        if self.cont > 1:
            title = f'Yucata.de Games ({self.cont})'
            description = 'More game links below'
        else:
            title = f'Yucata.de Games'
            description = 'Online gaming portal, free and without advertisements \
                where you may play more than 60 different games.'
        url = 'https://www.yucata.de/en'
        colour = 0x00305E
        embed = discord.Embed(
            title=title, description=description, colour=colour, url=url)
        embed.set_thumbnail(
            url='https://www.yucata.de/bundles/images/Logo.jpg')
        return embed

    def base_boite_embed(self):
        if self.cont > 1:
            title = f'Boîte à Jeux Games ({self.cont})'
            description = 'More game links below'
        else:
            title = f'Boîte à Jeux Games'
            description = 'Boîte à Jeux is a predominantly French online game system. The \
                interface has been translated to English and more recently, German as well.\
                \nGames are played in a web browser one turn at a time, which could take hours \
                or weeks, depending on the game and how often the players take their turns. \
                    Live games are possible if players are both logged in at the same time.'
        url = 'http://www.boiteajeux.net/'
        colour = 0x55774C
        embed = discord.Embed(
            title=title, description=description, colour=colour, url=url)
        embed.set_thumbnail(
            url='http://www.boiteajeux.net/img/banniere_baj_en.png')
        return embed

    def embed_constrain(
            self,
            name,
            value,
            embed,
            embeds,
            game=None,
            bga=None,
            yucata=None,
            boite=None):
        embeds.append(embed)
        if game:
            embed = self.base_embed(game)
        elif bga:
            embed = self.base_bga_embed()
        elif boite:
            embed = self.base_boite_embed()
        elif yucata:
            embed = self.base_yucata_embed()
        embed.add_field(name=name, value=value)
        return embed, embeds

    def format_game_embed(self, game):
        self.cont = 1
        embeds = []
        embed = self.base_embed(game)

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
            if len(link) > 1023:
                all_links = link.split('\n')
                count = 1
                value = ''
                for text in all_links:
                    name = 'Tabletopia ' + str(count) + ':'
                    if (len(value) +
                        len(text)) > 1022 or (len(value) +
                                              len(embed) > 5999):
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
                link = link.replace('\n', '; ')
                embed.add_field(name='Tabletopia', value=link)

        # Tabletop Simulator field
        if not game['tts']:
            embed.add_field(name='Tabletop Simulator', value='❌')
        else:
            link = game['tts']
            if len(link) > 1023:
                all_links = link.split('\n')
                count = 1
                value = ''
                for text in all_links:
                    name = 'Tabletop Simulator ' + str(count) + ':'
                    if (len(value) +
                        len(text)) > 1022 or (len(value) +
                                              len(embed) > 5999):
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
                link = link.replace('\n', '; ')
                embed.add_field(name='Tabletop Simulator', value=link)

        embeds.append(embed)

        return embeds

    def format_all_games_embed(self, bga=False, yucata=False, boite=False):
        self.cont = 1
        embeds = []
        if bga:
            embed = self.base_bga_embed()
        if yucata:
            embed = self.base_yucata_embed()
        if boite:
            embed = self.base_boite_embed()
        all_links = get_all_games(bga, yucata, boite)
        if all_links is None:
            return embeds
        count = 1
        alphabet = None
        value = ''
        for link, text in sorted(all_links.items()):
            name = link[0]
            if alphabet is None:
                alphabet = name
            if name != alphabet[0]:
                if (len(alphabet) + len(value) + len(embed)) > 5999:
                    count += 1
                    self.cont += 1
                    embed, embeds = self.embed_constrain(
                        alphabet, value, embed, embeds, bga=bga, yucata=yucata, boite=boite)
                else:
                    embed.add_field(name=alphabet, value=value)
                alphabet = name
                value = text
            else:
                if (len(alphabet) + len(value) + len(embed)) > 5998:
                    count += 1
                    self.cont += 1
                    embed, embeds = self.embed_constrain(
                        alphabet, value, embed, embeds, bga=bga, yucata=yucata, boite=boite)
                    alphabet = f'{name} (cont...)'
                    value = text
                elif (len(alphabet) + len(value) + len(text)) > 1022:
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

    async def embed_navigator(self, reaction, user, debug=False):
        emoji = reaction.emoji
        message = reaction.message
        if user.bot:
            return
        if emoji in ['⏮', '◀', '▶', '⏭']:
            title = message.embeds[0].title
            match = self.parser.search(title)
            if 'Board Game Arena Games' in title:
                if match is not None:
                    if debug:
                        print(f'> "{match[0]}" page matched')
                    idx = int(match[0].lstrip(' (').rstrip(')')) - 1
                else:
                    idx = 0
                responses = self.format_all_games_embed(bga=True)
            elif 'Boîte à Jeux' in title:
                if match is not None:
                    if debug:
                        print(f'> "{match[0]}" page matched')
                    idx = int(match[0].lstrip(' (').rstrip(')')) - 1
                else:
                    idx = 0
                responses = self.format_all_games_embed(boite=True)
            elif 'Yucata.de Games' in title:
                if match is not None:
                    if debug:
                        print(f'> "{match[0]}" page matched')
                    idx = int(match[0].lstrip(' (').rstrip(')')) - 1
                else:
                    idx = 0
                responses = self.format_all_games_embed(yucata=True)
            else:
                if match is not None:
                    if debug:
                        print(f'> "{match[0]}" page matched')
                    search_game = await search_web_board_game_data(
                        title.replace(str(match[0]), ''), message, reaction)
                    if debug:
                        print(f'> {title} is being fetched again')
                    idx = int(match[0].lstrip(' (').rstrip(')')) - 1
                else:
                    search_game = await search_web_board_game_data(title, message, reaction)
                    idx = 0
                responses = self.format_game_embed(search_game)

            if debug:
                print(f'Index is {idx}')
            old_idx = idx
            if emoji == '⏮':
                idx = 0
            elif emoji == '◀':
                idx = idx - 1
            elif emoji == '▶':
                idx = idx + 1
            elif emoji == '⏭':
                idx = len(responses) - 1

            if idx < 0:
                idx = 0
            elif idx > len(responses) - 1:
                idx = len(responses) - 1
            if debug:
                print(f'Index to return is {idx}')
                print(f'Total embeds: {len(responses)}')
            if idx != old_idx:
                await message.edit(content="", embed=responses[idx])
        else:
            return

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user, debug=False):
        await self.embed_navigator(reaction, user, debug=debug)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user, debug=False):
        await self.embed_navigator(reaction, user, debug=debug)

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
            return [response]
        else:
            response = 'Searching for ' + game_str + ', standby whilst I search online...'
            message = await ctx.send(response)
            search_game = await search_web_board_game_data(
                game_str, message, ctx)
            if search_game:
                responses = self.format_game_embed(search_game)
                await message.edit(content="", embed=responses[0])
                if len(responses) > 1:
                    emojis = ['⏮', '◀', '▶', '⏭']
                    for emoji in emojis:
                        await message.add_reaction(emoji)
                return responses
            else:
                response = game_str + ' not found online.'
                await message.edit(content=response)
                return [response]

    @commands.command(aliases=['board_game_arena'],
                      help='Prints the list of games currently available on Board Game Arena.')
    async def bga(self, ctx):
        response = 'Getting the list of BGA games...'
        message = await ctx.send(response)
        responses = self.format_all_games_embed(bga=True)
        await message.edit(content="", embed=responses[0])
        if len(responses) > 1:
            emojis = ['⏮', '◀', '▶', '⏭']
            for emoji in emojis:
                await message.add_reaction(emoji)
        return responses

    @commands.command(aliases=['boite_a_jeux', 'boîte', 'boîte_à_jeux'],
                      help='Prints the list of games currently available on Boîte à Jeux.')
    async def boite(self, ctx):
        response = 'Getting the list of Boîte à Jeux games...'
        message = await ctx.send(response)
        responses = self.format_all_games_embed(boite=True)
        await message.edit(content="", embed=responses[0])
        if len(responses) > 1:
            emojis = ['⏮', '◀', '▶', '⏭']
            for emoji in emojis:
                await message.add_reaction(emoji)
        return responses

    @commands.command(aliases=['yucata.de'],
                      help='Prints the list of games currently available on Yucata.de.')
    async def yucata(self, ctx):
        response = 'Getting the list of Yucata games...'
        message = await ctx.send(response)
        responses = self.format_all_games_embed(yucata=True)
        await message.edit(content="", embed=responses[0])
        if len(responses) > 1:
            emojis = ['⏮', '◀', '▶', '⏭']
            for emoji in emojis:
                await message.add_reaction(emoji)
        return responses

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

    @commands.command(help='Lists the help for command category `games`.',
                      pass_context=True)
    async def games(self, ctx):
        await ctx.invoke(self.bot.get_command('help'), 'games')


def setup(bot):
    bot.add_cog(Games(bot))

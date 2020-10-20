import discord
import json
import os
from discord.ext import commands
from online_game_search import search_web_board_game_data


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        dir_path = os.path.dirname(os.path.realpath(__file__))
        try:
            with open(os.path.join(dir_path, '../data/games.json')) as json_file:
                self.db = json.load(json_file)
        except FileNotFoundError:
            self.db = {}
            print(
                'games.json is empty, all results will need to use search functionality')

    def base_embed(self, game, cont=False):
        if cont:
            title = game['name'] + ' (continued)'
            description = 'More game links below'
        else:
            title = game['name']
            description = game['description']

        embed = discord.Embed(
            title=title, description=description)
        embed.set_thumbnail(url=game['image'])
        if not cont:
            bgg_text = '[' + game['name'] + '](' + game['bgg'] + ')'
            embed.add_field(name='Read more at BGG',
                            value=bgg_text, inline=False)
        return embed

    def embed_constrain(self, name, value, embed, embeds, game):
        embeds.append(embed)
        embed = self.base_embed(game, True)
        embed.add_field(name=name, value=value)
        return embed, embeds

    def format_embed(self, game):
        embeds = []
        embed = self.base_embed(game)

        # App field
        if not game['app']:
            embed.add_field(name='App:', value='❌')
        else:
            link = game['app']
            embed.add_field(name='App:', value=link)

        # Board Game Arena field
        if not game['bga']:
            embed.add_field(name='Board Game Arena:', value='❌')
        else:
            link = game['bga']
            embed.add_field(name='Board Game Arena:', value=link)

        # Boîte à Jeux field
        if not game['boite']:
            embed.add_field(name='Boîte à Jeux :', value='❌')
        else:
            link = game['boite']
            embed.add_field(name='Boîte à Jeux :', value=link)

        # Yucata field
        if not game['yucata']:
            embed.add_field(name='Yucata:', value='❌')
        else:
            link = game['yucata']
            embed.add_field(name='Yucata:', value=link)

        # Tabletopia field
        if not game['tabletopia']:
            embed.add_field(name='Tabletopia:', value='❌')
        else:
            link = game['tabletopia']
            if len(link) > 1023:
                all_links = link.split('\n')
                count = 1
                value = ''
                for text in all_links:
                    name = 'Tabletopia ' + str(count) + ':'
                    if (len(value) +
                        len(text)) > 1023 or (len(value) +
                                              len(embed) > 5999):
                        count += 1
                        if (len(value) + len(embed) > 5999):
                            embed, embeds = self.embed_constrain(
                                name, value, embed, embeds, game)
                        value = ''
                    else:
                        value += text
                        embed, embeds = self.embed_constrain(
                            name, value, embed, embeds, game)
                        value += '\n'
            else:
                embed.add_field(name='Tabletopia:', value=link)

        # Tabletop Simulator field
        if not game['tts']:
            embed.add_field(name='Tabletop Simulator:', value='❌')
        else:
            link = game['tts']
            if len(link) > 1023:
                all_links = link.split('\n')
                count = 1
                value = ''
                for text in all_links:
                    name = 'Tabletop Simulator ' + str(count) + ':'
                    if (len(value) +
                        len(text)) > 1023 or (len(value) +
                                              len(embed) > 5999):
                        embed, embeds = self.embed_constrain(
                            name, value, embed, embeds, game)
                        count += 1
                        value = ''
                    else:
                        value += text
                        value += '\n'
                embed, embeds = self.embed_constrain(name, value,
                                                     embed, embeds, game)
            else:
                embed.add_field(name='Tabletop Simulator:', value=link)

        embeds.append(embed)

        return embeds

    def have_game(self, game):
        try:
            for item in self.db['games']:
                if game.lower() in item['name'].lower():
                    return True
        except KeyError:
            # Don't crash on an empty db
            return False
        return False

    def get_game(self, game):
        # Get an exact match
        for item in self.db['games']:
            if game.lower() == item['name'].lower():
                return item
        # Failing that, return an approximate match
        for item in self.db['games']:
            if game.lower() in item['name'].lower():
                return item

    @commands.command(name='game',
                      help='Print detailed info about a board game. \
                          Use quotes if there is a space in the name')
    async def game(self, ctx, game=None):
        if game is None:
            response = f'Please enter a game to search: `m;game <game_name>`. '
            response += f'Use quotes if there is a space in the name. '
            response += f'\nNumber of games in database: **{len(self.db) - 1}**'
            await ctx.send(response)
            return
        if self.have_game(game):
            responses = self.format_embed(self.get_game(game))
            for response in responses:
                await ctx.send(embed=response)
        else:
            response = game + ' not found in my database, standby whilst I search online...'
            await ctx.send(response)
            search_game = search_web_board_game_data(game)
            if search_game:
                responses = self.format_embed(search_game)
                for response in responses:
                    await ctx.send(embed=response)
            else:
                response = game + ' not found online.'
                await ctx.send(response)


def setup(bot):
    bot.add_cog(Games(bot))

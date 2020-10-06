import discord
import json
import os
from discord.ext import commands
from online_game_search import search_web_board_game_data


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, '../data/games.json')) as json_file:
            self.db = json.load(json_file)

    def format_embed(self, game):
        embed = discord.Embed(
            title=game['name'], description=game['description'])
        embed.set_image(url=game['image'])
        bgg_text = '[' + game['name'] + '](' + game['bgg'] + ')'
        embed.add_field(name='Read more at BGG', value=bgg_text, inline=False)
        if not game['app']:
            embed.add_field(name='App:', value='❌')
        else:
            link = game['app']
            embed.add_field(name='App:', value=link)
        if not game['bga']:
            embed.add_field(name='Board Game Arena:', value='❌')
        else:
            link = game['bga']
            embed.add_field(name='Board Game Arena:', value=link)
        if not game['boite']:
            embed.add_field(name='Boîte à Jeux :', value='❌')
        else:
            link = game['boite']
            embed.add_field(name='Boîte à Jeux :', value=link)
        if not game['tabletopia']:
            embed.add_field(name='Tabletopia:', value='❌')
        else:
            link = game['tabletopia']
            embed.add_field(name='Tabletopia:', value=link)
        if not game['tts']:
            embed.add_field(name='Tabletop Simulator:', value='❌')
        else:
            link = game['tts']
            embed.add_field(name='Tabletop Simulator:', value=link)
        if not game['yucata']:
            embed.add_field(name='Yucata:', value='❌')
        else:
            link = game['yucata']
            embed.add_field(name='Yucata:', value=link)
        return embed

    def have_game(self, game):
        for item in self.db['games']:
            if game.lower() in item['name'].lower():
                return True
        return False

    def get_game(self, game):
        for item in self.db['games']:
            if game.lower() in item['name'].lower():
                return item

    @commands.command(name='game',
                      help='Print detailed info about a board game')
    async def game(self, ctx, game):
        if self.have_game(game):
            response = self.format_embed(self.get_game(game))
            await ctx.send(embed=response)
        else:
            response = game + " not found in my database, standby whilst I search online..."
            await ctx.send(response)
            response = self.format_embed(search_web_board_game_data(game))
            await ctx.send(embed=response)


def setup(bot):
    bot.add_cog(Games(bot))

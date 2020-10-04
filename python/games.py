import discord
import json
import os
from discord.ext import commands


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, '../data/games.json')) as json_file:
            self.db = json.load(json_file)

    def format_embed(self, game):
        embed = discord.Embed(title=game['name'])
        embed.add_field(name=game['bgg'],
                        value=game['description'][:1023], inline=True)
        return embed

    def have_game(self, game):
        for item in self.db['games']:
            if game.lower() in item['name'].lower():
                return True
        return False

    def get_game(self, game):
        for item in self.db['games']:
            if game in item['name']:
                return item

    @commands.command(name='game',
                      help='Print detailed info about a board game')
    async def game(self, ctx, game):
        if self.have_game(game):
            response = self.format_embed(self.get_game(game))
            await ctx.send(embed=response)
        else:
            response = game + " not in database"
            await ctx.send(response)


def setup(bot):
    bot.add_cog(Games(bot))

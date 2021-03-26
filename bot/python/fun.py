import discord
import json
import os
import random
from discord.ext import commands


class Fun(commands.Cog, name='fun'):
    '''
    Fun commands that aren't part of the bot proper.
    '''

    def __init__(self, bot):
        self.bot = bot
        dir_path = os.path.dirname(os.path.realpath(__file__))
        try:
            with open(os.path.join(dir_path, 'data/theme_data.json')) as json_file:
                self.theme_data = json.load(json_file)
        except FileNotFoundError:
            self.theme_data = {}
            print(
                'theme_data.json is empty. Can''t generate random themes.')

    @commands.command(aliases=['t'],
                      help='Generates a random board game theme.')
    async def theme(self, ctx):
        '''
        Makes a random board game concept from a style, a component and
         a setting. Taken from the JSON file, theme_data.json.
        '''
        response = random.choice(self.theme_data['styles']) + ' using ' +\
            random.choice(self.theme_data['components']) + ' set in ' +\
            random.choice(self.theme_data['settings'])
        await ctx.send(response)

    @commands.command(help='Lists the help for command category `fun`.',
                      pass_context=True)
    async def fun(self, ctx):
        await ctx.invoke(self.bot.get_command('help'), 'fun')


def setup(bot):
    bot.add_cog(Fun(bot))

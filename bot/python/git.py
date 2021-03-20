import discord
import os
from discord.ext import commands


class Git(commands.Cog, name='git'):
    '''
    Commands for displaying info about the git repo
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['contribute', 'repo'],
                      help='Prints info on the Github repo')
    async def github(self, ctx):
        '''
        Prints an embed that contains info on the Github repo
        '''
        title = 'boardgamebot GitHub Repo'
        description = 'The GitHub repo for this bot is \
            [tawilkinson/boardgamebot](https://github.com/tawilkinson/boardgamebot).\
            \nIf you find a bug or want to suggest a feature \
            [create a new issue](https://github.com/tawilkinson/boardgamebot/issues).\
            \nDocumentation is coming soon...'
        url = 'https://github.com/tawilkinson/boardgamebot'
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        file = discord.File(os.path.join(cur_dir, '../data/GitHub.png'))
        response = discord.Embed(
            title=title, description=description, url=url, colour=discord.Colour.lighter_grey())
        response.set_thumbnail(url='attachment://GitHub.png')
        await ctx.send('', embed=response, file=file)

    @commands.command(help='Lists the help for command category `git`.',
                      pass_context=True)
    async def git(self, ctx):
        await ctx.invoke(self.bot.get_command('help'), 'git')


def setup(bot):
    bot.add_cog(Git(bot))

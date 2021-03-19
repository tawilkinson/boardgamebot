import discord
import random
from discord.ext import commands


class Fun(commands.Cog, name='fun'):
    '''Fun commands that aren't part of the bot proper.'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['t'],
                      help='Generates a random board game theme.')
    async def theme(self, ctx):
        style = [
            'Eurogame',
            'Card game',
            'Roll & Write',
            'Strategy game',
            'Worker placement',
            'Engine builder',
            '4X',
            'Deck builder',
            'Abstract game',
            'Dexterity game',
            'Drafting game',
            'Roll & move',
            'Push-your-luck',
            'Social deduction']
        component = [
            'meeples',
            'legacy mechanics',
            'tableau',
            'area control',
            'hidden roles',
            'deck building',
            'rondels',
            'storytelling',
            'trick-taking',
            'hand management',
            'victory points',
            'tile placement',
            'drafting',
            'custom dice']
        setting = [
            'Istanbul',
            'Carcassonne',
            'London',
            'America',
            'a sushi restaurant',
            'Tokyo',
            'Warsaw',
            'a space ship',
            'the bottom of the ocean',
            'Birmingham',
            'a factory',
            'the world of Warhammer Fantasy Battles',
            'Waterdeep']

        response = random.choice(
            style) + ' using ' + random.choice(component) + ' set in ' + random.choice(setting)
        await ctx.send(response)

    @commands.command(help='Lists the help for command category `fun`.', pass_context=True)
    async def fun(self, ctx):
        await ctx.invoke(self.bot.get_command('help'), 'fun')


def setup(bot):
    bot.add_cog(Fun(bot))

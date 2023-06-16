import logging
import discord
from discord import app_commands
from discord.ext import commands
from utils.roller import Roller

logger = logging.getLogger('discord')


class Dice(commands.Cog, name='dice'):
    '''A simple dice roller.'''

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='roll', description='Roll up to 9,999 dice with up to 9,999 sides each')
    @app_commands.describe(roll_text='standard dic notation string. e.g. 2d20kl1|5d6+1')
    async def roll(self, interaction: discord.Interaction, roll_text: str) -> None:
        '''
        Using standard dice notation: You can roll up to 9,999 dice with up to 9,999 sides each.\n\
        Examples:\n- `bg roll <x>d20`: rolls <x> twenty sided die.\n- `bg roll 2d20kl1`: rolls 2 d20 and keeps \
            the lowest result, i.e. disadvantage.\n- `bg roll 2d20k1`: rolls 2 d20 and keeps \
            the highest result, i.e. advantage.\n- `bg roll 10d6!`: rolls 10 d6 and explodes when a 6 is rolled.\n\
            - `bg roll d6+5`: rolls a d6 and adds 5.\n- `bg roll d6-4`: rolls a d6 and subtracts 4.\n\
            - `bg roll d6|d8|d20`: rolls a d, a d8 and a d20. All above functionality is supported.\n
        '''
        roller = Roller(''.join(roll_text))
        responses = roller.roll()
        await interaction.response.send_message('You rolled:\n')
        final_response = ''
        for response in responses:
            if len(final_response) + len(response) > 1999:
                await interaction.channel.send(final_response)
                final_response = ''
            final_response += response
        await interaction.channel.send(final_response)

    @commands.command(help='Lists the help for command category `dice`',
                      pass_context=True)
    async def dice(self, ctx):
        await ctx.invoke(self.bot.get_command('help'), 'dice')


async def setup(bot):
    await bot.add_cog(Dice(bot))

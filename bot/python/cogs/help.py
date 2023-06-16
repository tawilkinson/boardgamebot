import discord
import logging
from discord import app_commands
from discord.ext import commands

# This custom help command is a perfect replacement for the default one on any Discord Bot written in Discord.py Rewrite!
# Inspired by Jared Newsom (AKA Jared M.F.) -
# https://gist.github.com/That-Kidd/432b028352a44e434dfd54e3676a6a85

logger = logging.getLogger('discord')


class Help(commands.Cog, name='help'):
    '''
    Prints the help message/DM.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        emoji = reaction.emoji
        message = reaction.message
        if user.bot:
            return
        if message.author.id is self.bot.user.id:
            if emoji == '✉':
                await user.send('', embed=message.embeds[0])

    @app_commands.command()
    @app_commands.describe(cog='Optional: name of a command to get help on')
    async def help(self, interaction: discord.Interaction, cog: str='all') -> None:
        '''
        Gets all cogs and commands of this bot.
        '''
        try:
            if cog == 'all':
                halp = discord.Embed(
                    title='Command Listing and Uncategorised Commands',
                    description='Click on ✉ to get this info via DM',
                    colour=discord.Colour.blurple())
                cogs_desc = ''
                halp.add_field(
                    name='Command Categories',
                    value='Use `/help cog:*category*` to find out more about them!',
                    inline=False)
                for x in self.bot.cogs:
                    halp.add_field(name=x,
                                   value=self.bot.cogs[x].__doc__,
                                   inline=True)
                if hasattr(interaction.user, 'guild_permissions') and interaction.user.guild_permissions.manage_guild:
                    # These are all bot admin commands
                    halp.add_field(
                        name='Uncategorised Commands',
                        value='',
                        inline=False)
                    for y in self.bot.walk_commands():
                        if not y.cog_name and not y.hidden:
                            halp.add_field(name=y.name,
                                        value=y.help,
                                        inline=True)
                await interaction.response.send_message('', embed=halp)
                if interaction.channel.type is not discord.ChannelType.private:
                    message = await interaction.original_response()
                    await message.add_reaction('✉')
            else:
                cog = cog.lower()
                if cog in self.bot.cogs:
                    halp = discord.Embed(
                        title=cog + ' Command Listing', description=self.bot.cogs[cog].__doc__,
                        colour=discord.Colour.blurple())
                    for c in self.bot.get_cog(cog).walk_commands():
                        if not c.hidden:
                            if c.name == cog:
                                name = f'help `cog:`{cog}'
                            else:
                                name = c.name 
                            halp.add_field(
                                name=name, value=c.help, inline=True)
                    for c in self.bot.get_cog(cog).walk_app_commands():
                        halp.add_field(
                            name=c.name, value=c.description, inline=True)
                else:
                    halp = discord.Embed(
                        title='Error!',
                        description='How do you even use "' +
                        cog + '"?',
                        colour=discord.Colour.red())

                await interaction.response.send_message('', embed=halp)
                if interaction.channel.type is not discord.ChannelType.private:
                    message = await interaction.original_response()
                    await message.add_reaction('✉')
        except Exception as e:
            if logger.level >= 10:
                logger.debug(e)


async def setup(bot):
    await bot.add_cog(Help(bot))

import discord
import logging
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

    @ commands.command()
    async def help(self, ctx, *cog):
        '''
        Gets all cogs and commands of this bot.
        '''
        try:
            if not cog:
                halp = discord.Embed(
                    title='Command Listing and Uncategorised Commands',
                    description='Click on ✉ to get this info via DM.',
                    colour=discord.Colour.blurple())
                cogs_desc = ''
                halp.add_field(
                    name='Command Categories',
                    value='Use `bg help *category*` to find out more about them!',
                    inline=False)
                for x in self.bot.cogs:
                    halp.add_field(name=x,
                                   value=self.bot.cogs[x].__doc__,
                                   inline=True)
                halp.add_field(
                    name='Uncategorised Commands',
                    value='Use `bg help *command*` to find out more about them!',
                    inline=False)
                for y in self.bot.walk_commands():
                    if not y.cog_name and not y.hidden:
                        halp.add_field(name=y.name,
                                       value=y.help,
                                       inline=True)
                message = await ctx.send('', embed=halp)
                if ctx.channel.type is not discord.ChannelType.private:
                    await message.add_reaction(emoji='✉')
            else:
                if cog[0] in self.bot.cogs:
                    halp = discord.Embed(
                        title=cog[0] + ' Command Listing', description=self.bot.cogs[cog[0]].__doc__,
                        colour=discord.Colour.blurple())
                    for c in self.bot.get_cog(cog[0]).get_commands():
                        if not c.hidden:
                            halp.add_field(
                                name=c.name, value=c.help, inline=True)
                else:
                    halp = discord.Embed(
                        title='Error!',
                        description='How do you even use "' +
                        cog[0] + '"?',
                        colour=discord.Colour.red())

                message = await ctx.send('', embed=halp)
                if ctx.channel.type is not discord.ChannelType.private:
                    await message.add_reaction(emoji='✉')
        except Exception as e:
            if logger.level >= 10:
                logger.debug(e)


def setup(bot):
    bot.add_cog(Help(bot))

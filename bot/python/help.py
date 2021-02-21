import discord
from discord.ext import commands
"""This custom help command is a perfect replacement for the default one on any Discord Bot written in Discord.py Rewrite!

Inspired by Jared Newsom (AKA Jared M.F.) - https://gist.github.com/That-Kidd/432b028352a44e434dfd54e3676a6a85"""


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user, debug=False):
        emoji = reaction.emoji
        message = reaction.message
        if user.bot:
            return
        if emoji == '✉':
            await user.send('', embed=message.embeds[0])

    @ commands.command()
    async def help(self, ctx, *cog, debug=False):
        """Gets all cogs and commands of this bot."""
        try:
            if not cog:
                halp = discord.Embed(title='Cog Listing and Uncatergorized Commands',
                                     description='Use `bg help *cog*` to find out more about them!\n\
                                         (BTW, the Cog Name Must Be in Title Case, Just Like this Sentence.)\
                                             \n\nClick on ✉ to get this info via DM.')
                cogs_desc = ''
                for x in self.bot.cogs:
                    cogs_desc += ('{} - {}'.format(x,
                                                   self.bot.cogs[x].__doc__)+'\n')
                halp.add_field(
                    name='Cogs', value=cogs_desc[0:len(cogs_desc)-1], inline=False)
                cmds_desc = ''
                for y in self.bot.walk_commands():
                    if not y.cog_name and not y.hidden:
                        cmds_desc += ('{} - {}'.format(y.name, y.help)+'\n')
                halp.add_field(name='Uncatergorized Commands',
                               value=cmds_desc[0:len(cmds_desc)-1], inline=False)
                message = await ctx.send('', embed=halp)
                await message.add_reaction(emoji='✉')
            else:
                if len(cog) > 1:
                    halp = discord.Embed(
                        title='Error!', description='That is way too many cogs!', color=discord.Color.red())
                    await ctx.send('', embed=halp)
                else:
                    found = False
                    for x in self.bot.cogs:
                        for y in cog:
                            if x == y:
                                halp = discord.Embed(
                                    title=cog[0]+' Command Listing', description=self.bot.cogs[cog[0]].__doc__)
                                for c in self.bot.get_cog(y).get_commands():
                                    if not c.hidden:
                                        halp.add_field(
                                            name=c.name, value=c.help, inline=False)
                                found = True
                    if not found:
                        halp = discord.Embed(
                            title='Error!', description='How do you even use "'+cog[0]+'"?', color=discord.Color.red())

                    message = await ctx.send('', embed=halp)
                    await message.add_reaction(emoji='✉')
        except Exception as e:
            if debug:
                print(e)


def setup(bot):
    bot.add_cog(Help(bot))

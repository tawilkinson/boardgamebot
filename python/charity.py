import discord
from discord.ext import commands


class Charity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='donate',
        help='Get the link to donate.')
    async def donate(self, ctx):
        title = 'Donate to Dementia UK!'
        description = 'We have partnered with Dementia UK\'s Raise your Game.'
        description += ' By taking part in Raise your Game and raising money '
        description += 'for Dementia UK, you will help dementia specialist '
        description += 'Admiral Nurses support more families facing dementia.'
        embed = discord.Embed(
            title=title, description=description)
        embed.add_field(
            name='Donate Now', value='[Board Game Fest on Just Giving](https://www.justgiving.com/fundraising/wilkosboardgamefest)')
        embed.set_thumbnail(
            url='https://www.dementiauk.org/wp-content/uploads/2020/07/RYG-hero-image.png')
        await ctx.send(embed=embed)

    @commands.command(
        name='charity',
        help='Get information on our chosen charity')
    async def charity(self, ctx):
        title = 'Dementia UK: Raise your Game'
        description = 'We have partnered with Dementia UK\'s Raise your Game.'
        description += ' By taking part in Raise your Game and raising money '
        description += 'for Dementia UK, you will help dementia specialist '
        description += 'Admiral Nurses support more families facing dementia.\n'
        description += '- **£33** could pay for a new Admiral Nurse to support a family in crisis with nowhere else to turn\n'
        description += '- **£125** could pay for an Admiral Nurse to answer calls for an evening on our Dementia Helpline, '
        description += 'when other sources of support have closed for the night\n'
        description += '- **£515** could pay for two Admiral Nurses to answer calls on our Dementia Helpline on Sundays, when families have nowhere else to turn to'
        embed = discord.Embed(
            title=title, description=description)
        value = '[Dementia UK](https://www.dementiauk.org/)\n'
        value += '[Raise your Game](https://www.dementiauk.org/get-involved/events-and-fundraising/raiseyourgame/)'
        embed.add_field(
            name='Learn More at Dementia UK', value=value)
        embed.add_field(
            name='Donate Now', value='[Board Game Fest on Just Giving](https://www.justgiving.com/fundraising/wilkosboardgamefest)')
        embed.set_thumbnail(
            url='https://www.dementiauk.org/wp-content/uploads/2020/07/Raise-your-Game-virtual-event-graphic-square.png')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Charity(bot))

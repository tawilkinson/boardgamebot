import discord
import DiscordUtils
import html2text
import logging
from discord.ext import commands
from utils.game import Webpage
from subprocess import check_output

logger = logging.getLogger('discord')


class Git(commands.Cog, name='git'):
    '''
    Commands for displaying info about the git repo
    '''

    def __init__(self, bot):
        self.bot = bot

    def get_release_text(self):
        '''
        Scrape all release info
        '''
        if logger.level >= 10:
            logger.debug('Getting Release info from Github')
        h = html2text.HTML2Text()
        release_page = Webpage(
            'https://github.com/tawilkinson/boardgamebot/releases')
        page = release_page.page_html
        versions = {}
        if page:
            search_results = page.find_all('div', class_='Box-body')
            for result in search_results:
                if result is not None:
                    title = result.select_one('a', class_='Link--primary').text
                    url = 'https://github.com' + \
                        result.select_one('a', class_='Link--primary').get('href')
                    release_md = str(result.find_all('div', class_='markdown-body')[0])
                    description = h.handle(release_md)
                    description = description.replace('* ', '')
                    description = description[:2000]
                    versions[title] = (description, url)
        else:
            title = 'Release page not found'
            description = 'There is an issue getting data from GitHub at the moment...'
            url = 'https://github.com/tawilkinson/boardgamebot/releases/latest'
            versions[title] = (description, url)

        return versions

    def generate_versions_embeds(self):
        '''
        Makes an embed for every version
        '''
        embeds = []
        versions = self.get_release_text()
        for version, info in versions.items():
            embed = discord.Embed(
                title=version,
                description=info[0],
                url=info[1],
                colour=discord.Colour.lighter_grey())
            embeds.append(embed)
        return embeds

    @commands.command(aliases=['changelog'],
                      help='Prints info on the current release')
    async def releases(self, ctx):
        '''
        Prints an embed that contains info on the current GitHub release
        '''
        responses = self.generate_versions_embeds()
        print(responses)
        paginator = DiscordUtils.Pagination.AutoEmbedPaginator(
            ctx, timeout=60, auto_footer=True)
        await paginator.run(responses)

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
        file = discord.File('data/GitHub.png')
        response = discord.Embed(
            title=title,
            description=description,
            url=url,
            colour=discord.Colour.lighter_grey())
        response.set_thumbnail(url='attachment://GitHub.png')
        await ctx.send('', embed=response, file=file)

    @commands.command(help='Lists the help for command category `git`.',
                      pass_context=True)
    async def git(self, ctx):
        await ctx.invoke(self.bot.get_command('help'), 'git')


async def setup(bot):
    await bot.add_cog(Git(bot))

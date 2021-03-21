import discord
import DiscordUtils
import html
import html2text
import os
from bs4 import BeautifulSoup
from discord.ext import commands
from online_game_search import Webpage


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
        h = html2text.HTML2Text()
        release_page = Webpage(
            'https://github.com/tawilkinson/boardgamebot/releases')
        page = release_page.page_html
        versions = {}
        if page:
            search_results = page.find_all('div', class_='release-entry')
            for result in search_results:
                title = result.find(
                    'div', class_='release-header').find('a').text
                url = 'https://github.com' + \
                    result.find(
                        'div', class_='release-header').find('a').get('href')
                release_md = str(result.find('div', class_='markdown-body'))
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
                title=version, description=info[0], url=info[1], colour=discord.Colour.lighter_grey())
            embeds.append(embed)
        return embeds

    @commands.command(aliases=['changelog'],
                      help='Prints info on the current release')
    async def releases(self, ctx):
        '''
        Prints an embed that contains info on the current GitHub release
        '''
        responses = self.generate_versions_embeds()
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

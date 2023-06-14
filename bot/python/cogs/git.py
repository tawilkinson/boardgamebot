import discord
import html2text
import logging
from discord import app_commands
from discord.ext import commands, menus
from utils.game import Webpage
from utils.menus import DiscordPages

logger = logging.getLogger('discord')

class VersionsEmbeds(menus.ListPageSource):
    '''
    Makes an embed for every version
    '''
    async def format_page(self, menu, version):
        embed = discord.Embed(
            title=version["title"],
            description=version["description"],
            url=version["url"],
            colour=discord.Colour.lighter_grey())
        return embed

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
        versions = []
        if page:
            search_results = page.find_all('div', class_='Box-body')
            for result in search_results:
                if result is not None:
                    title = result.select_one('a', class_='Link--primary').text
                    url = 'https://github.com' + \
                        result.select_one('a', class_='Link--primary').get('href')
                    release_md = str(
                        result.find_all(
                            'div', class_='markdown-body')[0])
                    description = h.handle(release_md)
                    description = description.replace('* ', '')
                    description = description[:2000]
                    versions.append({"title":title, "description":description, "url":url})
        else:
            title = 'Release page not found'
            description = 'There is an issue getting data from GitHub at the moment...'
            url = 'https://github.com/tawilkinson/boardgamebot/releases/latest'
            versions.append({"title":title, "description":description, "url":url})

        return versions

    @app_commands.command(name='releases', description='Prints info on the current release')
    async def releases(self, interaction: discord.Interaction) -> None:
        '''
        Prints an embed that contains info on the current GitHub release
        '''
        versions = self.get_release_text()
        formatter = VersionsEmbeds(versions, per_page=1)
        paginator = DiscordPages(formatter, timeout=60, auto_footer=True)
        await paginator.start(interaction)

    @app_commands.command(name='github', description='Prints info on the Github repo')
    async def github(self, interaction: discord.Interaction) -> None:
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
        await interaction.response.send_message('', embed=response, file=file)

    @commands.command(help='Lists the help for command category `git`.',
                      pass_context=True)
    async def git(self, ctx):
        await ctx.invoke(self.bot.get_command('help'), 'git')


async def setup(bot):
    await bot.add_cog(Git(bot))

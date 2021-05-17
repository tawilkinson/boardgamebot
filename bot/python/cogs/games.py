import discord
import DiscordUtils
import logging
import re
import string
import time
from discord.ext import tasks, commands
from utils.embeds import GameEmbed
from utils.online_game_search import search_web_board_game_data, get_all_games

logger = logging.getLogger('discord')


class Games(commands.Cog, name='games'):
    '''Board game search functions.'''

    def __init__(self, bot):
        self.bot = bot
        self.game_cacher.start()

    @tasks.loop(hours=24)
    async def game_cacher(self):
        # Every 24 hours, refresh the cache
        get_all_games(site=1)
        get_all_games(site=2)
        get_all_games(site=3)
        get_all_games(site=4)

    @game_cacher.before_loop
    async def before_cache(self):
        logger.debug(f'Waiting for bot to start before caching...')
        await self.bot.wait_until_ready()

    @commands.command(aliases=['g', 'search', 's', 'boardgame', 'bg'],
                      help='Fetches game info from [BGG](https://boardgamegeek.com/) \
                              then returns online sources, if they exist, to play \
                                  the game.')
    async def game(self, ctx, *game):
        start_time = time.time()
        if logger.level >= 10:
            logger.debug('+++ Starting Game Search +++')
        game_str = ' '.join(game)
        game_str = string.capwords(game_str)
        if game_str is None:
            response = f'Please enter a game to search: `bg game <game_name>`. '
            await ctx.send(response)
        else:
            response = 'Searching for ' + game_str + ', standby whilst I search online...'
            message = await ctx.send(response)
            search_game = await search_web_board_game_data(
                game_str, message, ctx)
            if logger.level >= 10:
                logger.debug('+++ Ending Game Search +++')
            if search_game:
                time_diff = time.time() - start_time
                embedder = GameEmbed(search_game)
                responses = embedder.format_game_embed(
                    search_game, full_time=time_diff)
                if len(responses) > 1:
                    paginator = DiscordUtils.Pagination.AutoEmbedPaginator(
                        ctx, timeout=60)
                    await paginator.run(responses)
                else:
                    await ctx.send(content='', embed=responses[0])
                await message.delete()

            else:
                response = game_str + ' not found online.'
                await message.edit(content=response)

    @commands.command(aliases=['board_game_arena', 'boardgamearena'],
                      help='Prints the list of games currently available on Board Game Arena.')
    async def bga(self, ctx):
        start_time = time.time()
        response = 'Getting the list of BGA games...'
        message = await ctx.send(response)
        embedder = GameEmbed(site=1)
        all_links = get_all_games(site=1)
        responses = embedder.format_all_games_embed(
            all_links, start_time=start_time)
        await message.delete()
        if len(responses) > 1:
            paginator = DiscordUtils.Pagination.AutoEmbedPaginator(
                ctx, timeout=60)
            await paginator.run(responses)
        else:
            await ctx.send(content='', embed=responses[0])

    @commands.command(
        aliases=[
            'boite_a_jeux',
            'boiteajeux',
            'boîte',
            'boîte_à_jeux',
            'boîteàjeux'],
        help='Prints the list of games currently available on Boîte à Jeux.')
    async def boite(self, ctx):
        start_time = time.time()
        response = 'Getting the list of Boîte à Jeux games...'
        message = await ctx.send(response)
        embedder = GameEmbed(site=2)
        all_links = get_all_games(site=2)
        responses = embedder.format_all_games_embed(
            all_links, start_time=start_time)
        await message.delete()
        if len(responses) > 1:
            paginator = DiscordUtils.Pagination.AutoEmbedPaginator(
                ctx, timeout=60)
            await paginator.run(responses)
        else:
            await ctx.send(content='', embed=responses[0])

    @commands.command(help='Tabletopia has over 1600 games, so prints a link to the all games page on Tabletopia.')
    async def tabletopia(self, ctx):
        description = 'Tabletopia has over 1600 games. Full list at [Tabletopia: All Games](https://tabletopia.com/games?page=1).'
        embed = discord.Embed(
            title='Tabletopia Games',
            description=description,
            colour=0xFD9705,
            url='https://tabletopia.com/games?page=1')
        embed.set_thumbnail(
            url='https://tabletopia.com/Content/Images/logo.png')
        await ctx.send(embed=embed)

    @commands.command(aliases=['tabletop_simulator', 'tabletopsimulator'],
                      help='Prints the list of DLC currently available for Tabletop Simulator.')
    async def tts(self, ctx):
        start_time = time.time()
        response = 'Getting the list of Tabletop Simulator DLC...'
        message = await ctx.send(response)
        embedder = GameEmbed(site=4)
        all_links = get_all_games(site=4)
        responses = embedder.format_all_games_embed(
            all_links, start_time=start_time)
        await message.delete()
        if len(responses) > 1:
            paginator = DiscordUtils.Pagination.AutoEmbedPaginator(
                ctx, timeout=60)
            await paginator.run(responses)
        else:
            await ctx.send(content='', embed=responses[0])

    @commands.command(aliases=['yucata.de'],
                      help='Prints the list of games currently available on Yucata.de.')
    async def yucata(self, ctx):
        start_time = time.time()
        response = 'Getting the list of Yucata games...'
        message = await ctx.send(response)
        embedder = GameEmbed(site=3)
        all_links = get_all_games(site=3)
        responses = embedder.format_all_games_embed(
            all_links, start_time=start_time)
        await message.delete()
        if len(responses) > 1:
            paginator = DiscordUtils.Pagination.AutoEmbedPaginator(
                ctx, timeout=60)
            await paginator.run(responses)
        else:
            await ctx.send(content='', embed=responses[0])

    @commands.command(help='Lists the help for command category `games`.',
                      pass_context=True)
    async def games(self, ctx):
        await ctx.invoke(self.bot.get_command('help'), 'games')


def setup(bot):
    bot.add_cog(Games(bot))

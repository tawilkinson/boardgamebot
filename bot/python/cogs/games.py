import discord
import logging
import string
import time
from discord import app_commands
from discord.ext import tasks, commands
from utils.embeds import GameEmbed, GameEmbeds
from utils.menus import DiscordPages
from utils.online_game_search import search_web_board_game_data, get_all_games

logger = logging.getLogger('discord')


class Games(commands.GroupCog, name='games'):
    '''Board game search functions.'''

    def __init__(self, bot):
        self.bot = bot
        self.game_cacher.start()

    @tasks.loop(hours=24)
    async def game_cacher(self):
        print("Game cache started")
        # Every 24 hours, refresh the cache
        get_all_games(site=1)
        get_all_games(site=2)
        get_all_games(site=3)
        get_all_games(site=4)
        print("Game cache ended")

    @game_cacher.before_loop
    async def before_cache(self):
        logger.debug(f'Waiting for bot to start before caching...')
        await self.bot.wait_until_ready()

    @app_commands.command(name='search', description='Fetches game info from \
                          BGG then returns online sources to play the game.')
    async def game_search(self, interaction: discord.Interaction, game: str) -> None:
        start_time = time.time()
        if logger.level >= 10:
            logger.debug('+++ Starting Game Search +++')
        game_str = string.capwords(game)
        response = 'Searching for ' + game_str + ', standby whilst I search online...'
        await interaction.response.send_message(response)
        message = await interaction.original_response()
        search_game = await search_web_board_game_data(
            game_str, message, interaction)
        if logger.level >= 10:
            logger.debug('+++ Ending Game Search +++')
        if search_game:
            embedder = GameEmbed(search_game)
            embedder.set_start_time(start_time)
            responses = embedder.format_game_embed()
            if len(responses) > 1:
                formatter = GameEmbeds(responses, per_page=1)
                paginator = DiscordPages(formatter, timeout=60, auto_footer=True, message=message)
                await paginator.start(interaction)
            else:
                await interaction.followup.send(content='', embed=responses[0])
            await message.delete()

        else:
            response = game_str + ' not found online.'
            await message.edit(content=response)

    @app_commands.command(name='boardgamearena',
                      description='Prints the list of games currently available on Board Game Arena.')
    async def game_bga(self, interaction: discord.Interaction) -> None:
        start_time = time.time()
        response = 'Getting the list of BGA games...'
        await interaction.response.send_message(response)
        message = await interaction.original_response()
        embedder = GameEmbed(site=1)
        embedder.set_start_time(start_time)
        all_links = get_all_games(site=1)
        responses = embedder.format_all_games_embed(all_links)
        await message.delete()
        if len(responses) > 1:
            formatter = GameEmbeds(responses, per_page=1)
            paginator = DiscordPages(formatter, timeout=60, auto_footer=True, message=message)
            await paginator.start(interaction)
        else:
            await interaction.followup.send(content='', embed=responses[0])

    @app_commands.command(name='boîte_à_jeux',
        description='Prints the list of games currently available on Boîte à Jeux.')
    async def game_boite(self, interaction: discord.Interaction) -> None:
        start_time = time.time()
        response = 'Getting the list of Boîte à Jeux games...'
        await interaction.response.send_message(response)
        message = await interaction.original_response()
        embedder = GameEmbed(site=2)
        embedder.set_start_time(start_time)
        all_links = get_all_games(site=2)
        responses = embedder.format_all_games_embed(all_links)
        await message.delete()
        if len(responses) > 1:
            formatter = GameEmbeds(responses, per_page=1)
            paginator = DiscordPages(formatter, timeout=60, auto_footer=True, message=message)
            await paginator.start(interaction)
        else:
            await interaction.followup.send(content='', embed=responses[0])

    @app_commands.command(name='tabletopia', description='Tabletopia has over 1600 games, so prints a link to the all games page on Tabletopia.')
    async def game_tabletopia(self, interaction: discord.Interaction) -> None:
        description = 'Tabletopia has over 1600 games. Full list at [Tabletopia: All Games](https://tabletopia.com/games?page=1).'
        embed = discord.Embed(
            title='Tabletopia Games',
            description=description,
            colour=0xFD9705,
            url='https://tabletopia.com/games?page=1')
        embed.set_thumbnail(
            url='https://tabletopia.com/Content/Images/logo.png')
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='tabletop_simulator',
                      description='Prints the list of DLC currently available for Tabletop Simulator.')
    async def game_tts(self, interaction: discord.Interaction) -> None:
        start_time = time.time()
        response = 'Getting the list of Tabletop Simulator DLC...'
        await interaction.response.send_message(response)
        message = await interaction.original_response()
        embedder = GameEmbed(site=4)
        embedder.set_start_time(start_time)
        all_links = get_all_games(site=4)
        responses = embedder.format_all_games_embed(all_links)
        await message.delete()
        if len(responses) > 1:
            formatter = GameEmbeds(responses, per_page=1)
            paginator = DiscordPages(formatter, timeout=60, auto_footer=True, message=message)
            await paginator.start(interaction)
        else:
            await interaction.followup.send(content='', embed=responses[0])

    @app_commands.command(name='yucata_de',
                      description='Prints the list of games currently available on Yucata.de.')
    async def game_yucata(self, interaction: discord.Interaction) -> None:
        start_time = time.time()
        response = 'Getting the list of Yucata games...'
        await interaction.response.send_message(response)
        message = await interaction.original_response()
        embedder = GameEmbed(site=3)
        embedder.set_start_time(start_time)
        all_links = get_all_games(site=3)
        responses = embedder.format_all_games_embed(all_links)
        await message.delete()
        if len(responses) > 1:
            formatter = GameEmbeds(responses, per_page=1)
            paginator = DiscordPages(formatter, timeout=60, auto_footer=True, message=message)
            await paginator.start(interaction)
        else:
            await interaction.followup.send(content='', embed=responses[0])

    @commands.command(help='Lists the help for command category `games`.',
                      pass_context=True)
    async def games(self, ctx):
        await ctx.invoke(self.bot.get_command('help'), 'games')


async def setup(bot):
    await bot.add_cog(Games(bot))

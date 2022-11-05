# bot.py
import asyncio
import logging
import os
import sys
import traceback
import discord
from discord.ext import commands
from dotenv import load_dotenv


logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# You need a token to connect to discord. We load this from
# .env is it exists.
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
# Debugging
debug = bool(os.getenv('DEBUG'))
if debug:
    print('Setting DEBUG log level')
    logger.setLevel(logging.DEBUG)

# Setup intents
intents = discord.Intents.default()
intents.guilds = True
intents.message_content=True
intents.reactions=True
intents.members=True

# this specifies what extensions to load when the bot starts up
startup_extensions = ['fun', 'games', 'dice', 'help', 'git', 'wordle']
# set the bot prefix read by Discord
bot = commands.Bot(command_prefix='bg ', intents=intents)
# We are going to use help.py to add an embed help.
# Remove basic help command here.
bot.remove_command('help')

@bot.event
async def on_ready():
    '''
    Report that we can actually connect to Discord
    '''
    print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_message(message):
    '''
    It's a fun gif
    '''
    if message.author == bot.user:
        return
    if ('gameboard' in message.content.lower()) or (
            'game board' in message.content.lower()):
        response = 'https://gfycat.com/thismixeddonkey'
        await message.channel.send(response)
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    '''
    Returns a truncated error when a command fails.
    Makes it easier to debug errors in chat.
    '''
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('No such command. Try using `bg help` to see valid commands.')
    else:
        # Better traceback to stdout for debugging
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr)
        await ctx.send(f'An error was raised, ask the bot devs:\n```{error}```')


@bot.command()
@commands.has_permissions(manage_guild=True)
async def load(ctx, cog_name: str):
    '''
    Loads a cog.
    '''
    try:
        await bot.load_extension(f'cogs.{cog_name}')
    except (AttributeError, ImportError) as e:
        await ctx.send('```py\n{}: {}\n```'.format(type(e).__name__, str(e)))
        return
    except discord.ext.commands.ExtensionAlreadyLoaded:
        await ctx.send('{} already loaded.'.format(cog_name))
        return
    await ctx.send('{} loaded.'.format(cog_name))


@bot.command()
@commands.has_permissions(manage_guild=True)
async def unload(ctx, cog_name: str):
    '''
    Unloads a cog.
    '''
    try:
        await bot.unload_extension(f'cogs.{cog_name}')
        await ctx.send('{} unloaded.'.format(cog_name))
    except discord.ext.commands.ExtensionNotLoaded:
        await ctx.send('{} not loaded.'.format(cog_name))


@bot.command()
@commands.has_permissions(manage_guild=True)
async def reload(ctx, cog_name: str):
    '''
    Reloads a cog.
    '''
    await unload(ctx, cog_name)
    await load(ctx, cog_name)


async def setup_bot():
    # Load all the extensions from the list above
    for extension in startup_extensions:
        try:
            await bot.load_extension(f'cogs.{extension}')
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

async def main():
    async with bot:
        await setup_bot()
        # Start the bot!
        await bot.start(TOKEN)


if __name__ == '__main__':
    asyncio.run(main())

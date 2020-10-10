# bot.py
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# this specifies what extensions to load when the bot starts up
startup_extensions = ['theme', 'agenda', 'games']

bot = commands.Bot(command_prefix='m;')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if ('gameboard' in message.content.lower()) or (
            'game board' in message.content.lower()):
        response = 'https://gfycat.com/thismixeddonkey'
        await message.channel.send(response)
    await bot.process_commands(message)


@bot.command()
async def load(ctx, cog_name: str):
    '''Loads a cog.'''
    try:
        bot.load_extension(cog_name)
    except (AttributeError, ImportError) as e:
        await ctx.send('```py\n{}: {}\n```'.format(type(e).__name__, str(e)))
        return
    await ctx.send('{} loaded.'.format(cog_name))


@bot.command()
async def unload(ctx, cog_name: str):
    '''Unloads a cog.'''
    bot.unload_extension(cog_name)
    await ctx.send('{} unloaded.'.format(cog_name))


@bot.command()
async def reload(ctx, cog_name: str):
    '''Reloads a cog.'''
    await unload(ctx, cog_name)
    await load(ctx, cog_name)

if __name__ == '__main__':
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

    bot.run(TOKEN)

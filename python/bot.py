# bot.py
import os
import random

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="m;")


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if ("gameboard" in message.content.lower()) or (
            "game board" in message.content.lower()):
        response = "https://gfycat.com/thismixeddonkey"
        await message.channel.send(response)
    await bot.process_commands(message)


@bot.command(name="theme", help="Generates a random board game theme")
async def theme(ctx):
    style = [
        "Eurogame",
        "Card game",
        "Roll & Write",
        "Strategy game",
        "Worker placement",
        "Engine builder",
        "4X",
        "Deck builder",
        "Abstract game",
        "Dexterity game",
        "Drafting game",
        "Roll & move",
        "Push-your-luck",
        "Social deduction"]
    component = [
        "meeples",
        "legacy mechanics",
        "tableau",
        "area control",
        "hidden roles",
        "deck building",
        "rondels",
        "storytelling",
        "trick-taking",
        "hand management",
        "victory points",
        "tile placement",
        "drafting",
        "custom dice"]
    setting = [
        "Istanbul",
        "Carcassonne",
        "London",
        "America",
        "a sushi restaurant",
        "Tokyo",
        "Warsaw",
        "a space ship",
        "the bottom of the ocean",
        "Birmingham",
        "a factory",
        "the world of Warhammer Fantasy Battles",
        "Waterdeep"]

    response = random.choice(
        style) + " using " + random.choice(component) + " set in " + random.choice(setting)
    await ctx.send(response)

bot.run(TOKEN)

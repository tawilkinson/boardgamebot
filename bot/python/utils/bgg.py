import asyncio
import collections
import discord
import logging
import lxml
import html
import difflib
from utils.game import Webpage

logger = logging.getLogger("discord")


def bgg_data_from_id(game, game_id):
    """
    Takes an item of Game class and a known BGG id. Sets relevant
    game data from the BGG page referenced by id.
    """
    bgg_url = game.get_set_bgg_url(game_id)
    if logger.level >= 10:
        logger.debug(f">>> {game.name} on BGG: {bgg_url}")
    bgg_page = Webpage(bgg_url, xml=True)
    if bgg_page.page_html.items.description:
        game_description = html.unescape(bgg_page.page_html.items.description.text)
        abridged_game_description = f"{game_description[0:300]} ..."
        game.set_description(abridged_game_description)
        if logger.level >= 10:
            logger.debug(f"--> retrieved {game.name} description")
        if bgg_page.page_html.items.image:
            game_image = bgg_page.page_html.items.image.text
            game.set_image(game_image)
            if logger.level >= 10:
                logger.debug(f"--> retrieved {game.name} image")
        if logger.level >= 10:
            logger.debug(f"--> retrieved {game.name} Board Game Geek data")
        return True
    return False


async def select_game(game, possible_board_games, ctx):
    """
    Selects a game if a valid int is sent as a message
    """

    def check(m):
        """
        Checks message is by original command user, in the same channel
        and is a number
        """
        try:
            _ = int(m.content)
        except ValueError:
            return False
        if m.channel != ctx.channel:
            return False
        if m.author != ctx.author:
            return False
        return True

    difflib_closest = difflib.get_close_matches(
        game.name, possible_board_games.keys(), 1, 0
    )[0]

    try:
        msg = await ctx.client.wait_for("message", timeout=30, check=check)
        if msg:
            idx = int(msg.content) - 1
            key = list(possible_board_games.keys())[idx]
            closest_match = possible_board_games[key]["name"]
            game.update_name(closest_match)
            if ctx.channel.type is not discord.ChannelType.private:
                await msg.delete()
        else:
            game.update_name(difflib_closest)
            closest_match = difflib_closest
    except asyncio.TimeoutError:
        game.update_name(difflib_closest)
        closest_match = difflib_closest
    return closest_match, key


async def get_bgg_data(game, message, ctx, exact=True):
    """
    Takes an object of "Game" Class and searches Board Game Geeks API for a boardgame
    that exactly matches the Game name. Will update the Game Object with url for
    the webpage of the game on BBGs website, as well as the Game's image, and description.
    """
    game_id = 0
    if exact:
        if logger.level >= 10:
            logger.debug(f">>> Board Game Geek: {game.bgg_search_url}")
        bgg_search = Webpage(game.bgg_search_url, xml=True)
    else:
        if logger.level >= 10:
            logger.debug(f">>> Board Game Geek: {game.bgg_non_exact_search_url}")
        bgg_search = Webpage(game.bgg_non_exact_search_url, xml=True)
    if bgg_search.page_html is None:
        return False
    if bgg_search.page_html.items is not None:
        games_found = bgg_search.page_html.items["total"]

        if games_found == "0":
            game.set_description(
                "Game not found on Board Game Geek! Is it even a board game?"
            )
            if logger.level >= 10:
                logger.debug(f"!!! {game.name} not found on Board Game Geek !!!")
        elif int(games_found) > 1:
            closest_match = None
            board_game_search = bgg_search.page_html.items.findAll("item")
            print(board_game_search)
            possible_board_games = collections.OrderedDict()
            count = 0
            title = "Ambiguous Game Name"
            description = ""
            response = discord.Embed(
                title=title,
                description=description,
                colour=discord.Colour.dark_purple(),
            )
            for game_search in board_game_search:
                count += 1
                possible_name = game_search.find("name").get("value")
                possible_year = game_search.find("yearpublished").get("value")
                possible_board_games[game_search["id"]] = {
                    "name": possible_name,
                    "year": possible_year,
                }
                name = f"{count}: {possible_name}"
                value = f"{possible_year}"
                if (len(response) + len(name) + len(value)) > 5999:
                    break
                else:
                    response.add_field(name=name, value=value)
            description = (
                f"{len(possible_board_games)} potential matches on Board Game Geek."
            )
            description += (
                "\nPlease respond with the number of the game you were looking for..."
            )
            response.description = description
            if logger.level >= 10:
                logger.debug(
                    f"--> found {len(possible_board_games)} potential matches on Board Game Geek"
                )

            await message.edit(content="", embed=response)

            closest_match, key = await select_game(game, possible_board_games, ctx)

            if closest_match:
                if logger.level >= 10:
                    logger.debug(f"--> {closest_match} is closest match")
                if key:
                    return bgg_data_from_id(game, key)
                game.update_name(closest_match)
                game_id = possible_board_games[closest_match]["id"]
                return bgg_data_from_id(game, game_id)
            return False
        else:
            game_id = bgg_search.page_html.items.item["id"]
            return bgg_data_from_id(game, game_id)
    else:
        if ctx and exact:
            await ctx.send("BBG Unreachable. Is BGG online?")
    if logger.level >= 10:
        logger.debug(f"--> {bgg_search.error}")
    return False

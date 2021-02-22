import discord
import json
import os
import re
from discord.ext import commands
from online_game_search import search_web_board_game_data


class Games(commands.Cog):
    '''Board game search functions.'''

    def __init__(self, bot):
        self.bot = bot
        self.cont = 1
        self.end_regex = r'\s\([0-9]+\)$'
        self.parser = re.compile(self.end_regex)

    def base_embed(self, game):
        if self.cont > 1:
            title = game['name'] + f' ({self.cont})'
            description = 'More game links below'
        else:
            title = game['name']
            description = game['description'][:2047]

        embed = discord.Embed(
            title=title, description=description)
        embed.set_thumbnail(url=game['image'])
        if self.cont == 1:
            bgg_text = '[' + game['name'] + '](' + game['bgg'] + ')'
            embed.add_field(name='Read more at BGG',
                            value=bgg_text, inline=False)
        return embed

    def embed_constrain(self, name, value, embed, embeds, game):
        embeds.append(embed)
        embed = self.base_embed(game)
        embed.add_field(name=name, value=value)
        return embed, embeds

    def format_embed(self, game):
        self.cont = 1
        embeds = []
        embed = self.base_embed(game)

        # App field
        if not game['app']:
            embed.add_field(name='App:', value='❌')
        else:
            link = game['app']
            embed.add_field(name='App:', value=link)

        # Board Game Arena field
        if not game['bga']:
            embed.add_field(name='Board Game Arena:', value='❌')
        else:
            link = game['bga']
            embed.add_field(name='Board Game Arena:', value=link)

        # Boîte à Jeux field
        if not game['boite']:
            embed.add_field(name='Boîte à Jeux :', value='❌')
        else:
            link = game['boite']
            embed.add_field(name='Boîte à Jeux :', value=link)

        # Yucata field
        if not game['yucata']:
            embed.add_field(name='Yucata:', value='❌')
        else:
            link = game['yucata']
            embed.add_field(name='Yucata:', value=link)

        # Tabletopia field
        if not game['tabletopia']:
            embed.add_field(name='Tabletopia:', value='❌')
        else:
            link = game['tabletopia']
            if len(link) > 1023:
                all_links = link.split('\n')
                count = 1
                value = ''
                for text in all_links:
                    name = 'Tabletopia ' + str(count) + ':'
                    if (len(value) +
                        len(text)) > 1023 or (len(value) +
                                              len(embed) > 5999):
                        count += 1
                        self.cont += 1
                        if (len(value) + len(embed) > 5999):
                            embed, embeds = self.embed_constrain(
                                name, value, embed, embeds, game)
                        value = ''
                    else:
                        value += text
                        embed, embeds = self.embed_constrain(
                            name, value, embed, embeds, game)
                        value += '\n'
            else:
                embed.add_field(name='Tabletopia:', value=link)

        # Tabletop Simulator field
        if not game['tts']:
            embed.add_field(name='Tabletop Simulator:', value='❌')
        else:
            link = game['tts']
            if len(link) > 1023:
                all_links = link.split('\n')
                count = 1
                value = ''
                for text in all_links:
                    name = 'Tabletop Simulator ' + str(count) + ':'
                    if (len(value) +
                        len(text)) > 1023 or (len(value) +
                                              len(embed) > 5999):
                        self.cont += 1
                        embed, embeds = self.embed_constrain(
                            name, value, embed, embeds, game)
                        count += 1
                        value = ''
                    else:
                        value += text
                        value += '\n'
                self.cont += 1
                embed, embeds = self.embed_constrain(name, value,
                                                     embed, embeds, game)
            else:
                embed.add_field(name='Tabletop Simulator:', value=link)

        embeds.append(embed)

        return embeds

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user, debug=False):
        emoji = reaction.emoji
        message = reaction.message
        if user.bot:
            return
        if emoji in ['⏮', '◀', '▶', '⏭']:
            title = message.embeds[0].title
            match = self.parser.search(title)
            if match is not None:
                if debug:
                    print(f'> "{match[0]}" page matched')
                search_game = search_web_board_game_data(
                    title.replace(str(match[0]), ''))
                if debug:
                    print(f'> {title} is being fetched again')
                idx = int(match[0].lstrip(' (').rstrip(')')) - 1
            else:
                search_game = search_web_board_game_data(title)
                idx = 0
            responses = self.format_embed(search_game)

            if debug:
                print(f'Index is {idx}')
            if emoji == '⏮':
                idx = 0
            elif emoji == '◀':
                idx = idx - 1
            elif emoji == '▶':
                idx = idx + 1
            elif emoji == '⏭':
                idx = len(responses) - 1

            if idx < 0:
                idx = 0
            elif idx > len(responses):
                idx = len(responses)
            if debug:
                print(f'Index to return is {idx}')
            await message.edit(content="", embed=responses[idx])
        else:
            return

    @commands.command(aliases=['g', 'search', 's', 'boardgame', 'bg'],
                      help='Print detailed info about a board game. \
                          Fetches game info from [BGG](https://boardgamegeek.com/) \
                              then returns online sources, if they exist, to play \
                                  the game.')
    async def game(self, ctx, *game):
        game_str = ' '.join(game)
        if game_str is None:
            response = f'Please enter a game to search: `bg game <game_name>`. '
            await ctx.send(response)
            return [response]
        else:
            response = 'Searching for ' + game_str + ', standby whilst I search online...'
            message = await ctx.send(response)
            search_game = search_web_board_game_data(game_str)
            if search_game:
                responses = self.format_embed(search_game)
                await message.edit(content="", embed=responses[0])
                if len(responses) > 1:
                    emojis = ['⏮', '◀', '▶', '⏭']
                    for emoji in emojis:
                        await message.add_reaction(emoji)
                return responses
            else:
                response = game_str + ' not found online.'
                await message.edit(content=response)
                return [response]


def setup(bot):
    bot.add_cog(Games(bot))

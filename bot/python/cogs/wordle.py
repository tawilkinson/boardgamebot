import asyncio
import discord
import logging
from discord.ext import commands
from utils.wordle_helpers import check_answer, get_emoji_word, get_word, get_wordle_stats, wordle_exception, valid_word
from utils.helpers import get_british_spellings_from_file, get_word_set_from_file, get_regional_indicator_letters_from_file

# Based on the $wordle command of https://github.com/sonmi451/friendly-aisha-clone
# Co-written by tawilkinson, sonm451 and ElectricWarr

logger = logging.getLogger('discord')

ALPHABET = [x for x in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']
BRITISH_WORDS = get_british_spellings_from_file()
REGIONAL_INDICATOR_LETTERS = get_regional_indicator_letters_from_file()
WORD_SET = get_word_set_from_file()


def embed_wordle(response_dict):
    robot_response = discord.Embed()
    for item, value in response_dict.items():
        robot_response.add_field(name=item,
                                 value=value,
                                 inline=False)
    return robot_response


async def wait_for_answer(ctx, word, word_len, word_set, emoji_letters, alphabet):
    emoji_correct_word = get_emoji_word(word, emoji_letters)
    tag_user = ctx.author.mention

    def check(m):
        '''
        Checks message is by original command user and in the same channel
        '''
        if m.channel != ctx.channel:
            return False
        if m.author != ctx.author:
            return False
        return True
    try:
        correct = False
        fail_count = 0
        leftover_alphabet = alphabet
        past_guesses = []
        while not correct:
            msg = await ctx.bot.wait_for('message', timeout=500, check=check)
            player = f'{msg.author}'
            player_title = f'{player.split("#")[0]}\'s Wordle!'
            guess = msg.content.lower()
            emoji_guess_word = get_emoji_word(
                msg.content.lower(), emoji_letters)
            if msg:
                if guess.split(' ')[0] == 'bg':
                    # Skip bot commands
                    pass
                elif not valid_word(guess, word_set):
                    wordle_invalid_word = {
                        player_title: f'{emoji_guess_word} is not in the dictionary. Please guess again.'}
                    await ctx.send(content=tag_user, embed=embed_wordle(wordle_invalid_word))
                else:
                    correct, wrong_len, leftover_alphabet, squares_response = check_answer(
                        guess, word, leftover_alphabet)
                    # Setup only for valid guesses
                    if not wrong_len:
                        fail_count += 1
                        emoji_alphabet = get_emoji_word(
                            ''.join(leftover_alphabet),
                            emoji_letters)
                        past_guesses += [f'{emoji_guess_word} | {squares_response}']
                        past_guesses_string = '\n'.join(past_guesses)
                        common_response_text = f'{past_guesses_string} - {fail_count}/{word_len+1}'
                    # Respond
                    if correct:
                        wordle_success = {
                            player_title: f'{common_response_text}',
                            'Correct!': f'The word was {emoji_correct_word}'}
                        await ctx.send(content=tag_user, embed=embed_wordle(wordle_success))
                        return
                    elif wrong_len:
                        wordle_bad_word = {
                            player_title: f'Your guesses must be {word_len} letters long! Try again!'}
                        await ctx.send(content=tag_user, embed=embed_wordle(wordle_bad_word))
                    elif (fail_count == word_len + 1):
                        wordle_fail = {
                            player_title: f'{common_response_text}',
                            'Incorrect!': f'The correct word was {emoji_correct_word}'}
                        await ctx.send(content=tag_user, embed=embed_wordle(wordle_fail))
                        break
                    else:
                        wordle_guess_again = {
                            player_title: f'{common_response_text}',
                            'Unused Letters': emoji_alphabet}
                        await ctx.send(content=tag_user, embed=embed_wordle(wordle_guess_again))
    except asyncio.TimeoutError:
        wordle_timeout_error = {
            'A wordley timeout': f'Guess quicker next time!\nThe word was {emoji_correct_word}'}
        await ctx.send(content=tag_user, embed=embed_wordle(wordle_timeout_error))


class Wordle(commands.Cog, name='wordle'):
    '''
    Play Wordle in Discord!
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def wordle(self, ctx, *message):
        if message:
            if message[0] == "stats":
                response = embed_wordle(
                    {"Wordle Stats": get_wordle_stats(message, WORD_SET)}
                )
                await ctx.send(embed=response)
                return
            try:
                word_len = int(message[0])
            except BaseException:
                word_len = 5
        else:
            word_len = 5
        try:
            word = get_word(BRITISH_WORDS, WORD_SET, word_len).upper()
            response = embed_wordle(
                {'Wordle!': f'Guessing a {word_len} character word in {word_len+1} guesses...'})
            await ctx.send(embed=response)
            await wait_for_answer(ctx, word, word_len, WORD_SET, REGIONAL_INDICATOR_LETTERS, ALPHABET)
        except Exception as error:
            if logger.level >= 10:
                response_text = ' Debug mode error details:\n```' + \
                    str(error) + '```'
            response_text = wordle_exception(error, logger.level)
            response = embed_wordle({'A wordley error!': response_text})
            await ctx.send(embed=response)


async def setup(bot):
    await bot.add_cog(Wordle(bot))

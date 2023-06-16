import asyncio
import discord
import logging
from discord import app_commands
from discord.ext import commands
from utils.embeds import embed_wordle
from utils.wordle_helpers import (
    check_answer,
    get_emoji_word,
    get_word,
    get_wordle_stats,
    wordle_exception,
    valid_word,
    count_wordle_field_length,
)
from utils.helpers import (
    get_british_spellings_from_file,
    get_word_set_from_file,
    get_regional_indicator_letters_from_file,
)

# Based on the $wordle command of https://github.com/sonmi451/friendly-aisha-clone
# Co-written by tawilkinson, sonm451 and ElectricWarr

logger = logging.getLogger("discord")

ALPHABET = [x for x in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
BRITISH_WORDS = get_british_spellings_from_file()
REGIONAL_INDICATOR_LETTERS = get_regional_indicator_letters_from_file()
WORD_SET = get_word_set_from_file()


async def wait_for_answer(
    interaction, word, word_len, word_set, emoji_letters, alphabet
):
    emoji_correct_word = get_emoji_word(word, emoji_letters)
    tag_user = interaction.user.mention

    def check(m):
        """
        Checks message is by original command user and in the same channel
        """
        if m.channel != interaction.channel:
            return False
        if m.author != interaction.user:
            return False
        return True

    try:
        correct = False
        fail_count = 0
        leftover_alphabet = alphabet
        past_guesses = []
        while not correct:
            msg = await interaction.client.wait_for("message", timeout=500, check=check)
            player = f"{msg.author}"
            player_title = f'{player.split("#")[0]}\'s Wordle!'
            guess = msg.content.lower()
            emoji_guess_word = get_emoji_word(msg.content.lower(), emoji_letters)
            if msg:
                if guess.split(" ")[0] == "bg":
                    # Skip bot commands
                    pass
                elif not valid_word(guess, word_set):
                    wordle_invalid_word = {
                        player_title: f"{emoji_guess_word} is not in the dictionary. Please guess again."
                    }
                    await interaction.followup.send(
                        content=tag_user, embed=embed_wordle(wordle_invalid_word)
                    )
                else:
                    (
                        correct,
                        wrong_len,
                        leftover_alphabet,
                        squares_response,
                    ) = check_answer(guess, word, leftover_alphabet)
                    # Setup only for valid guesses
                    if not wrong_len:
                        fail_count += 1
                        emoji_alphabet = get_emoji_word(
                            "".join(leftover_alphabet), emoji_letters
                        )
                        current_guess_string = (
                            f"{emoji_guess_word} | {squares_response}"
                        )
                        old_field_length = count_wordle_field_length(
                            past_guesses,
                            emoji_guess_word,
                            squares_response,
                            fail_count,
                            word_len,
                        )
                        if (old_field_length) >= 1024:
                            # don't add too much to the field
                            past_guesses.pop(0)
                        past_guesses += [current_guess_string]
                        past_guesses_string = "\n".join(past_guesses)
                        common_response_text = (
                            f"{past_guesses_string} - {fail_count}/{word_len+1}"
                        )
                    # Respond
                    if correct:
                        wordle_success = {
                            player_title: f"{common_response_text}",
                            "Correct!": f"The word was {emoji_correct_word}",
                        }
                        await interaction.followup.send(
                            content=tag_user, embed=embed_wordle(wordle_success)
                        )
                        return
                    elif wrong_len:
                        wordle_bad_word = {
                            player_title: f"Your guesses must be {word_len} letters long! Try again!"
                        }
                        await interaction.followup.send(
                            content=tag_user, embed=embed_wordle(wordle_bad_word)
                        )
                    elif fail_count == word_len + 1:
                        wordle_fail = {
                            player_title: f"{common_response_text}",
                            "Incorrect!": f"The correct word was {emoji_correct_word}",
                        }
                        await interaction.followup.send(
                            content=tag_user, embed=embed_wordle(wordle_fail)
                        )
                        break
                    else:
                        wordle_guess_again = {
                            player_title: f"{common_response_text}",
                            "Unused Letters": emoji_alphabet,
                        }
                        await interaction.followup.send(
                            content=tag_user, embed=embed_wordle(wordle_guess_again)
                        )
    except asyncio.TimeoutError:
        wordle_timeout_error = {
            "A wordley timeout": f"Guess quicker next time!\nThe word was {emoji_correct_word}"
        }
        await interaction.followup.send(
            content=tag_user, embed=embed_wordle(wordle_timeout_error)
        )


class Wordle(commands.GroupCog, name="wordle"):
    """
    Play Wordle in Discord!
    """

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="play", description="Play wordle in Discord")
    @app_commands.describe(
        word_length="Optional: length of the word for you wordle game. [Default: 5]"
    )
    async def wordle_play(
        self, interaction: discord.Interaction, word_length: int = 5
    ) -> None:
        try:
            word = get_word(BRITISH_WORDS, WORD_SET, word_length).upper()
            response = embed_wordle(
                {
                    "Wordle!": f"Guessing a {word_length} character word in {word_length+1} guesses..."
                }
            )
            await interaction.response.send_message(embed=response)
            await wait_for_answer(
                interaction,
                word,
                word_length,
                WORD_SET,
                REGIONAL_INDICATOR_LETTERS,
                ALPHABET,
            )
        except Exception as error:
            if logger.level >= 10:
                response_text = " Debug mode error details:\n```" + str(error) + "```"
            response_text = wordle_exception(error, logger.level)
            response = embed_wordle({"A wordley error!": response_text})
            await interaction.response.send_message(embed=response)

    @app_commands.command(
        name="stats", description="Get information on the wordle dictionary"
    )
    @app_commands.describe(
        word_length="Optional: get a count of the number of words of word_length [Default: 5]"
    )
    async def wordle_stats(
        self, interaction: discord.Interaction, word_length: int = 5
    ) -> None:
        response = embed_wordle(
            {"Wordle Stats": get_wordle_stats(WORD_SET, word_length)}
        )
        await interaction.response.send_message(embed=response)
        return


async def setup(bot):
    await bot.add_cog(Wordle(bot))

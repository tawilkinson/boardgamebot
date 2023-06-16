import emoji
import re
import random


def britishify(string, british_to_american, word_len):
    for british_spelling, american_spelling in british_to_american.items():
        if string == american_spelling:
            string = re.sub(
                f"(?<![a-zA-Z]){american_spelling}(?![a-z-Z])", british_spelling, string
            )
    if len(string) == word_len:
        return string
    else:
        return get_word(british_to_american, word_len)


def check_answer(answer, word, leftover_alphabet):
    characters = list(answer.upper())
    squares_response = ""
    if len(characters) == len(word):
        correct = True
        wrong_len = False
        idx = 0
        leftover_alphabet = [x for x in leftover_alphabet if x not in characters]
        for letter in characters:
            if letter == word[idx]:
                squares_response += "🟩"
            elif letter in word:
                correct = False
                squares_response += "🟦"
            else:
                correct = False
                squares_response += "⬛"
            idx += 1
    else:
        correct = False
        wrong_len = True
    return correct, wrong_len, leftover_alphabet, squares_response


def get_emoji_word(word, regional_indicator_letters):
    emojied_word = [
        regional_indicator_letters.get(char.lower())
        if regional_indicator_letters.get(char.lower())
        else char
        for char in word
    ]
    return " ".join(emojied_word)


def get_word(british_to_american, word_set, word_len=5):
    wordle_words = [word for word in word_set if len(word) == word_len]
    chosen_word = None
    while chosen_word is None:
        random_word = random.choice(wordle_words)
        if not random_word[0].isupper():
            chosen_word = random_word
    random_word = britishify(random_word, british_to_american, word_len)
    return random_word


def get_wordle_stats(word_set, word_len):
    stats_msg = (
        f"Play Wordle on Discord with a selection of {len(word_set)} English words!"
    )
    wordle_words = [word for word in word_set if len(word) == word_len]
    stats_msg += f"\nThere are {len(wordle_words)} English words with {word_len} letters in the Wordle dictionary."

    return stats_msg


def valid_word(word, word_set):
    if word in word_set:
        return True
    else:
        return False


def wordle_exception(error, debug):
    if debug >= 10:
        response_text = " Debug mode error details:\n```" + str(error) + "```"
        print("\nException in play_wordle():", error, "", sep="\n")
    else:
        response_text = (
            " Sorry your current game is lost forever, please start a new one!"
        )
    return response_text


def count_wordle_field_length(
    past_guesses, emoji_guess_word, squares_response, fail_count, word_len
):
    count = 7
    for item in past_guesses:
        count += len(emoji.demojize(item))

    count += len(emoji.demojize(emoji_guess_word))
    count += len(emoji.demojize(squares_response))
    count += len(str(fail_count))
    count += len(str(word_len))
    return count

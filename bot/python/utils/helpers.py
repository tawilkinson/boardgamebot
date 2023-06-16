import json
from enum import Enum


class Site(Enum):
    bga = 1
    boite = 2
    yucata = 3
    tts = 4


def get_int(value):
    """
    Returns an int if value can be an int
    """
    try:
        int_val = int(str(value))
        return int_val
    except (ValueError, TypeError) as e:
        return None


# This caches words to speed up the bot


def get_word_set_from_file():
    with open("data/words.json") as file:
        word_set = json.load(file)
    return word_set


def get_british_spellings_from_file():
    with open("data/british_spellings.json") as file:
        british_spellings = json.load(file)
    return british_spellings


def get_regional_indicator_letters_from_file():
    with open("data/emoji_letters.json") as file:
        regional_indicator_letters = json.load(file)
    return regional_indicator_letters

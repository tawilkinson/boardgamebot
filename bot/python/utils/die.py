import logging
import random
import re
from utils.helpers import get_int

logger = logging.getLogger("discord")


class Die:
    """
    Die Class which is instantiated with the text string used to call the roller
    command. Uses regex to analyse the input and then rolls dice on it.
    """

    def __init__(self, die_text):
        # Setup regex string
        self.dice_regex = r"(?P<count>\d{1,4})?d(?P<sides>\d{1,4})(?P<explode>!)?"
        self.dice_regex += r"(?P<keep>kl?(?P<keepCount>\d{1,2}))?((?P<plus>\+)?"
        self.dice_regex += r"(?P<minus>-)?(?P<mod>\d{1,2})|$)"
        self.parser = re.compile(self.dice_regex)
        self.match = self.parser.search(die_text.lower())
        # Setup variables used across Die commands
        self.rolls = []
        self.die_str = ""
        self.short_str = ""
        self.exploded = False
        self.total = 0
        self.explode = False
        self.plus = False
        self.minus = False
        self.parse_dice()
        # Make the roll
        try:
            self.roll()
        except AttributeError:
            self.die_str = "**! Incorrect syntax !**\n"
            self.short_str = self.die_str

    def parse_dice(self):
        """
        Try to get the various parts of the roll from the regex
        """
        self.count = get_int(self.match.group("count"))
        self.sides = get_int(self.match.group("sides"))
        if self.match.group("explode") == "!":
            self.explode = True
        self.keep = self.match.group("keep")
        self.keep_count = get_int(self.match.group("keepCount"))
        if self.match.group("plus") == "+":
            self.plus = True
        if self.match.group("minus") == "-":
            self.minus = True
        self.mod = get_int(self.match.group("mod"))

    def roll_core(self):
        """
        The core rolling function.
        """
        if self.sides > 0:
            result = random.randint(1, self.sides)
            if self.explode and result == self.sides:
                self.rolls.append(self.roll_explodes(result))
            else:
                self.rolls.append([result, str(result)])
        else:
            self.rolls.append([0, "0"])

    def roll_explodes(self, first_result):
        """
        Handle exploding dice rolls.
        """
        self.exploded = True
        result = first_result
        explode_str = "["
        roll = first_result
        explode_str += str(first_result)
        while result == first_result:
            result = random.randint(1, first_result)
            roll += result
            explode_str += " + " + str(result)
        explode_str += "]"

        return [roll, explode_str]

    def discard(self):
        """
        When we choose to keep lower (kl) or keep higher (k)
        dice rolls this function discards the other results and
        generates a sting with stikethrough text to display this.
        """
        if self.keep:
            if "kl" in self.keep:
                self.rolls = sorted(self.rolls)
            elif "k" in self.keep:
                self.rolls = sorted(self.rolls, reverse=True)
            self.strikethrough_discards()
        else:
            for result in self.rolls:
                self.total += result[0]

    def strikethrough_discards(self):
        """
        Adds strikethrough formatting to missed rolls
        """
        counter = 0
        for idx, value in enumerate(self.rolls):
            counter += 1
            if counter > self.keep_count:
                self.rolls[idx][1] = "~~" + value[1] + "~~"
            else:
                self.total += value[0]

    def generate_die_str(self, short=False):
        """
        Generates the string for a dice roll
        """
        str_text = ""
        if short:
            str_text += self.rolls[0][1]
            str_text += " + ... + "
            str_text += self.rolls[-1][1]

        else:
            for idx, roll in enumerate(self.rolls):
                str_text += roll[1]
                if idx < len(self.rolls) - 1:
                    str_text += " + "

        return str_text

    def roll(self):
        """
        Main dice rolling function. Uses the variables from
        the regex above to work out which rolling functions to
        call.
        """
        if self.count:
            # Roll mutliple dice
            for _ in range(self.count):
                self.roll_core()
        else:
            # Roll one die
            self.roll_core()
        # Discard rolls if needed
        self.discard()

        self.handle_multiple_strs()
        self.handle_mod_strs()

        # Generate the total string
        self.die_str += f"**{self.total}**"
        self.short_str += f"**{self.total}**"

        self.handle_keep_strs()
        self.handle_explode_strs()

        self.die_str += "\n"
        self.short_str += "\n"

    def handle_multiple_strs(self):
        """
        Multiple rolls need to be displayed nicely
        """
        if len(self.rolls) > 1:
            self.die_str = "_"
            self.die_str += self.generate_die_str()
            if self.mod:
                self.die_str += "_"
                self.short_str += "_" + self.generate_die_str(True) + "_"
            else:
                self.die_str += "_ = "
                self.short_str += "_" + self.generate_die_str(True) + "_ = "

    def handle_mod_strs(self):
        """
        Handle static positive/negative modifiers
        """
        if self.mod:
            if len(self.rolls) == 1:
                self.die_str = self.rolls[0][1]
                self.short_str = self.rolls[0][1]
            if self.plus:
                self.total += self.mod
                self.die_str += f" + {self.mod}"
            if self.minus:
                self.total -= self.mod
                self.die_str += f" - {self.mod}"
            self.die_str += " = "

    def handle_keep_strs(self):
        """
        Add emojis for keep/keep lower
        """
        if self.keep:
            if "kl" in self.keep:
                self.die_str = "👎 " + self.die_str + " 👎"
                self.short_str = "👎 " + self.short_str + " 👎"
            elif "k" in self.keep:
                self.die_str = "👍 " + self.die_str + " 👍"
                self.short_str = "👍 " + self.short_str + " 👍"

    def handle_explode_strs(self):
        """
        Adds emojis for exploding dice
        """
        if self.exploded:
            self.die_str = "💥 " + self.die_str + " 💥"
            self.short_str = "💥 " + self.short_str + " 💥"

    def reroll(self):
        """
        Re-rolls a die
        """
        self.die_str = ""
        self.total = 0
        self.exploded = False
        self.roll()

    def get_str(self):
        """
        Returns the die string
        """
        return self.die_str

    def get_short_str(self):
        """
        Returns the short die string
        """
        return self.short_str

    def get_len(self):
        """
        Utility function of get length of die_str
        """
        return len(self.die_str)

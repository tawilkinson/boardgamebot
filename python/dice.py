import discord
import random
import re
from discord.ext import commands


class Die():
    def __init__(self, die_text):
        self.dice_regex = r'(?P<count>\d{1,4})?d(?P<sides>\d{1,4})(?P<explode>!)?'
        self.dice_regex += r'(?P<keep>kl?(?P<keepCount>\d{1,2}))?((?P<plus>\+)?'
        self.dice_regex += r'(?P<minus>-)?(?P<mod>\d{1,2})|$)'
        self.parser = re.compile(self.dice_regex)
        self.match = self.parser.search(die_text)
        try:
            self.count = int(self.match.group('count'))
        except TypeError:
            self.count = False
        try:
            self.sides = int(self.match.group('sides'))
        except TypeError:
            self.sides = False
        if self.match.group('explode') == '!':
            self.explode = True
        else:
            self.explode = False
        self.keep = self.match.group('keep')
        try:
            self.keep_count = int(self.match.group('keepCount'))
        except TypeError:
            self.keep_count = False
        if self.match.group('plus') == '+':
            self.plus = True
        else:
            self.plus = False
        if self.match.group('minus') == '-':
            self.minus = True
        else:
            self.minus = False
        try:
            self.mod = int(self.match.group('mod'))
        except TypeError:
            self.mod = False
        self.rolls = []
        self.die_str = ''
        self.short_str = ''
        self.total = 0
        self.roll()

    def roll_core(self):
        if self.sides > 0:
            result = random.randint(1, self.sides)
            if self.explode and result == self.sides:
                self.rolls.append(result)
                self.roll_core()
            else:
                self.rolls.append(result)
        else:
            self.rolls[0] = '0'

    def discard(self):
        counter = 0
        if self.keep == 'k':
            self.rolls = sorted(self.rolls, reverse=True)
        elif self.keep == 'kl':
            self.rolls = sorted(self.rolls)
        if self.keep:
            for value in self.rolls:
                counter += 1
                if counter >= self.keep_count:
                    value = '~~' + value + '~~'
                else:
                    self.total += value
        else:
            for result in self.rolls:
                self.total += result

    def roll(self):
        print(f'self.count: {self.count}')
        if self.count:
            for num in range(self.count):
                self.roll_core()
        else:
            self.roll_core()
        self.discard()

        print(self.rolls)

        if len(self.rolls) > 1:
            self.die_str = '_'
            self.die_str += ' + '.join(str(roll) for roll in self.rolls) + '_'
            self.die_str += ' = '
            self.short_str += f'_{self.rolls[0]} + ... + {self.rolls[-1]}_ = '

        if self.mod:
            if self.plus:
                self.total += self.mod
                self.die_str += f' _+ {self.mod}_'
            if self.minus:
                self.total -= self.mod
                self.die_str += f' _- {self.mod}_'

        self.die_str += f'**{self.total}**\n'
        self.short_str += f'**{self.total}**\n'

    def reroll(self):
        self.die_str = ''
        self.total = 0
        self.roll()

    def get_str(self):
        return self.die_str

    def get_short_str(self):
        return self.short_str

    def get_len(self):
        return len(self.die_str)


class Roller():
    def __init__(self, roll_text):
        self.all_rolls = roll_text.split('|')

    def roll(self):
        responses = []

        for roll in self.all_rolls:
            die = Die(roll)
            if len(self.all_rolls) > 1:
                if (die.get_len() + len(roll)) > 1987:
                    responses.append(f'`{roll}` = ' + die.get_short_str())
                else:
                    responses.append(f'`{roll}` = ' + die.get_str())
            else:
                if die.get_len() > 1987:
                    responses.append(die.get_short_str())
                else:
                    responses.append(die.get_str())

        return responses


class Dice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @ commands.command(name='roll', help='Using standard dice notation: You can roll up to 9,999 dice with up to 9,999 sides each.')
    async def theme(self, ctx, roll_text):
        roller = Roller(roll_text)
        responses = roller.roll()
        final_response = 'You rolled:\n'
        for response in responses:
            if len(final_response) + len(response) > 1999:
                await ctx.send(final_response)
                final_response = ''
            final_response += response
        await ctx.send(final_response)


def setup(bot):
    bot.add_cog(Dice(bot))

import logging
from utils.die import Die

logger = logging.getLogger('discord')


class Roller():
    '''
    Roller class that splits up multiple rolls and then uses the
    Die class to roll each individual roll
    '''

    def __init__(self, roll_text):
        '''
        Splits incoming rolls into separate commands
        '''
        self.all_rolls = roll_text.split('|')

    def roll(self):
        '''
        Makes the rolls and setup multiple response messages
        if needed
        '''
        responses = []

        if len(self.all_rolls) == 1:
            die = Die(self.all_rolls[0])
            print(die.get_len)
            if die.get_len() > 1987:
                responses.append(die.get_short_str())
            else:
                responses.append(die.get_str())
            return responses

        for roll in self.all_rolls:
            die = Die(roll)
            # 1999 - 12 for 'You Rolled:'
            if (die.get_len() + len(roll)) > 1987:
                responses.append(f'`{roll}` = ' + die.get_short_str())
            else:
                responses.append(f'`{roll}` = ' + die.get_str())

        return responses

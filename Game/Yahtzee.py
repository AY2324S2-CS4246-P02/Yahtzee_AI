import numpy as np
from random import choice
from typing import List

DIE_CHOICES = [i for i in range(1, 7)]

NUM_DICE = 5
NUM_CATEGORIES = 14
NUM_UPPER = 6  # number of upper categories
MAX_REROLLS = 3  # includes initial roll
BONUS_THRESHOLD = 63
EMPTY = np.iinfo(np.uint8).max  # = 255

class Yahtzee:

    def __init__(self):
        # Stage setup.
        self.dice = np.zeros(NUM_DICE, dtype=np.uint8)
        self.scoresheet = np.full(NUM_CATEGORIES, EMPTY, dtype=np.uint8)
        self.log = np.empty((NUM_CATEGORIES, 3), dtype=object)
        # Log is (NUM_CATEGORIES x 3) array where:
        #       First column: Category chosen
        #       Second column: Score written
        #       Third column: Result of dice rolls (1 to 3 rolls) done in that round.
        # Bonus point is logged immediately at last row when achieved, with thirdrow showing the round it was achieved.
        # If bonus point is not achieved, the last row will be empty.

        # Initial dice roll.
        self.round = 0
        self.rerolls = MAX_REROLLS
        self.__roll_dice(np.arange(NUM_DICE))


    def __roll_dice(self, indices):
        """
        Rolls the dice of specified indices.
        Use get_dice() to see the result of the dice roll.
        Throws an exception if there are no more rerolls left, or when the game is over.
        """
        if self.rerolls == 0:
            raise Exception("You have no rerolls left.")
        if  self.round >= NUM_CATEGORIES - 1:
            raise Exception("Game is already over.")
        
        # Randomly choose numbers for dice roll.
        for index in indices:
            self.dice[index] = choice(DIE_CHOICES)
        
        # Logging result of dice roll.
        if self.log[self.round, 2] == None:
            self.log[self.round, 2] = [self.dice]
        else:
            self.log[self.round, 2].append(self.dice)
        
        self.rerolls -= 1


    def get_dice(self):
        return self.dice


    def get_available_categories(self):
        """
        Returns indices of all available (non-written) categories.
        Returns empty list if all categories are written and game is over.
        """
        available_categories = np.nonzero(self.scoresheet != EMPTY)
        return available_categories


    def write_score(self, category):
        """
        Writes into the score sheet at the category specified with the current dice roll.
        Automatically writes in and logs Bonus category if conditions satisfied.
        Returns 0 if successfully written (final score cannot be 0 because of Choice category).
        Returns the final score of the game if game is over.
        Throws an exception if attempted to write in Bonus category or already written category.
        """
        if category == NUM_CATEGORIES:
            raise Exception("You cannot write in Bonus category.")
        if self.scoresheet[category] != EMPTY:
            raise Exception("Category already written.")
        if self.round >= NUM_CATEGORIES - 1:
            raise Exception("Game is already over.")
        
        # Calculate score.
        score = 0  # 0 if not applicable
        check = CATEGORIES_CHECK[category]
        if check(self.dice):
            scoring = CATEGORIES_SCORING[category]
            score = scoring(self.dice)
        
        # Write in the score.
        self.scoresheet[category] = score
        self.log[self.round, 0] = CATEGORIES_NAMES[category]
        self.log[self.round, 1] = score

        # Check for Bonus category.
        upper_score = np.sum(self.scoresheet[0:NUM_UPPER])
        if upper_score >= BONUS_THRESHOLD:
            self.scoresheet[NUM_CATEGORIES] = CATEGORIES_SCORING[NUM_CATEGORIES]
            self.log[NUM_CATEGORIES, 0] = CATEGORIES_NAMES[NUM_CATEGORIES]
            self.log[NUM_CATEGORIES, 1] = CATEGORIES_SCORING[NUM_CATEGORIES]
            self.log[NUM_CATEGORIES, 2] = self.round

        # Set up for next round.
        self.round += 1
        self.rerolls = MAX_REROLLS
        if self.round >= NUM_CATEGORIES - 1:
            return self.calculate_score()
        else:
            # Rerolls the next round dice (not a choice).
            self.__roll_dice(self.dice, np.arange(NUM_DICE))
            return 0


    def calculate_score(self):
        """
        Calculates total score of the current score sheet.
        """
        total_score = np.sum(self.scoresheet)
        return total_score


# Category names.
# Note that Bonus category is always the last.
CATEGORIES_NAMES = [
    'Ones',
    'Twos',
    'Threes',
    'Fours',
    'Fives',
    'Sixes',
    'Three-of-a-Kind',
    'Four-of-a-Kind',
    'Full House',
    'Small Straight',
    'Large Straight',
    'Yahtzee',
    'Chance',
    'Bonus',
]


CATEGORIES_SCORING = [
    lambda dice: dice.count(1),
    lambda dice: dice.count(2),
    lambda dice: dice.count(3),
    lambda dice: dice.count(4),
    lambda dice: dice.count(5),
    lambda dice: dice.count(6),
    lambda dice: sum(dice),
    lambda dice: sum(dice),
    lambda dice: 25,
    lambda dice: 30,
    lambda dice: 40,
    lambda dice: 50,
    lambda dice: sum(dice),
    lambda dice: 35
]


CATEGORIES_CHECK = [
    lambda dice: True,
    lambda dice: True,
    lambda dice: True,
    lambda dice: True,
    lambda dice: True,
    lambda dice: True,
    lambda dice: max([dice.count(die) for die in set(dice)]) >= 3,
    lambda dice: max([dice.count(die) for die in set(dice)]) >= 4,
    lambda dice: (max([dice.count(die) for die in set(dice)]) == 3 and 
                  min([dice.count(die) for die in set(dice)]) == 2),
    lambda dice: (all([sorted(dice)[i - 1] == die - 1 for i, die in enumerate(sorted(dice))[:4]]) or
                  all([sorted(dice)[i - 1] == die - 1 for i, die in enumerate(sorted(dice))[1:]])),
    lambda dice: all([sorted(dice)[i - 1] == die - 1 for i, die in enumerate(sorted(dice))]),
    lambda dice: len(set(dice)) == 1,
    lambda dice: True,
    lambda dice: True
]


CATEGORIES = dict(
    [(name, (score, check)) for name, score, check in zip(
        CATEGORIES_NAMES,
        CATEGORIES_SCORING,
        CATEGORIES_CHECK
    )]
)
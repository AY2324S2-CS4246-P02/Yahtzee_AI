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
        self.scoresheet[CATEGORY_NAME2ID['Bonus']] = 0  # Bonus category should be initialized to 0 not EMPTY
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
        self.roll_dice(np.array([False, False, False, False, False]))

    def reset(self):
        self.round = 0
        self.rerolls = MAX_REROLLS
        self.scoresheet = np.full(NUM_CATEGORIES, EMPTY, dtype=np.uint8)
        self.log = np.empty((NUM_CATEGORIES, 3), dtype=object)
        self.roll_dice(np.array([False, False, False, False, False]))
        
    # State: Tuple(dice: list, rerolls: int, available_categories: list)
    def getCurrentState(self):
        return (tuple(self.dice.tolist()), self.rerolls, tuple(self.get_available_categories()))
    
    # Returns nextState and rewards
    # Action: Tuple(Literal['REROLL', 'KEEP'], Union[List[bool], str])
    def doAction(self, action):
        rewards = 0
        # If action KEEP, calculate score as set it as reward
        if action[0] == "KEEP":
            rewards = self.getScore(action[1])
            self.write_score(action[1])
        else:
            self.roll_dice(action[1])
        return (tuple(self.dice.tolist()), self.rerolls, tuple(self.get_available_categories())), rewards

    # Get the score for the chosen category
    def getScore(self, category_id):
        potential_scores = self.potential_score()
        # print("Potential Scores:", potential_scores)
        return potential_scores[category_id]
    
    def roll_dice(self, indices):
        """
        Takes in a list of integers of index ranging from 0 to number of dice.
        Rolls the dice of specified indices.
        Use get_dice() to see the result of the dice roll.
        Throws an exception if there are no more rerolls left, or when the game is over.
        """
        if self.rerolls == 0:
            raise Exception("You have no rerolls left.")
        if  self.round >= NUM_CATEGORIES - 1:
            raise Exception("Game is already over.")
        
        # Randomly choose numbers for dice roll.
        # TRUE MEANS TO KEEP; FALSE MEANS TO REROLL
        for i, choose in enumerate(indices[:5]):
            if not choose:
                self.dice[i] = choice(DIE_CHOICES)
        
        # Logging result of dice roll.
        if self.log[self.round, 2] == None:
            self.log[self.round, 2] = [self.dice]
        else:
            self.log[self.round, 2].append(self.dice)
        
        self.rerolls -= 1


    def get_dice(self):
        return self.dice
    
    
    def get_rerolls(self):
        return self.rerolls
    

    def get_round(self):
        return self.round
    

    def get_scoresheet(self):
        return self.scoresheet


    def potential_score(self):
        """
        Returns a scoresheet of potential score added if a category chosen is to be written with current dice.
        By definition, upper section categories' scores also include bonus point if satisfied.
        If the category is already filled, it is set to -1.
        """
        potential_sheet = np.full((NUM_CATEGORIES - 1), -1, int)
        for category in range(NUM_CATEGORIES - 1):
            if self.scoresheet[category] != EMPTY:
                continue
            score = 0
            check = CATEGORIES_CHECK[category]
            if check(self.dice):
                scoring = CATEGORIES_SCORING[category]
                score = scoring(self.dice)
            # Bonus check for upper section.
            if category < NUM_UPPER:
                segment = self.scoresheet[0:NUM_UPPER]
                bonus_check = np.sum(segment[segment != EMPTY]) + score
                # print("Bonus Check:", bonus_check)
                if bonus_check >= BONUS_THRESHOLD:
                    score += CATEGORIES_SCORING[NUM_CATEGORIES-1](self.dice)
            potential_sheet[category] = score
        return potential_sheet
    
    def get_display_scoresheet(self):
        ## If a category is available, displays "--- (POTENTIAL_SCORE)"
        ## If a category is not available, displays ACTUAL_SCORE
        sheet = []
        for idx, (p, a) in enumerate(zip(self.potential_score(), self.scoresheet)):
            if p == -1:
                sheet.append(str(a))
            else:
                sheet.append(f"--- ({p})")
        sheet.append(self.get_bonus())
        sheet.append(self.calculate_score())

        return sheet
    
    ## To be deprecated once bug in bonus score calculation is fixed
    def get_bonus(self):
        s = 0
        for i in self.scoresheet[:6]:
            s += (i if i != 255 else 0)
        return 0 if s < 63 else 35

    def get_available_categories(self):
        """
        Returns indices of all available (non-written) categories.
        Returns empty list if all categories are written and game is over.
        """
        available_categories = np.nonzero(self.scoresheet == EMPTY)[0].tolist()
        if NUM_CATEGORIES-1 in available_categories:
            available_categories.remove(NUM_CATEGORIES-1)
        return available_categories


    def write_score(
            self,
            category: int,
            dice: np.ndarray = None):
        """
        Writes into the score sheet at the category with the current dice roll or specified dice.
        Automatically writes in and logs Bonus category if conditions satisfied.
        Throws an exception if attempted to write in Bonus category or already written category.

        Parameters:
        category (int): Integer of category index to write in.
        dice (np.array of int): Dice to calculate score with (will be logged), set to current dice if unspecified.

        Returns:
        int: 0 if successfully written (final score cannot be 0 because of Choice category).
        int: Final score of the game if game is over.
        """
        if category == NUM_CATEGORIES:
            raise Exception("You cannot write in Bonus category.")
        if self.scoresheet[category] != EMPTY:
            raise Exception("Category already written.")
        if self.round >= NUM_CATEGORIES - 1:
            raise Exception("Game is already over.")
        
        if type(dice) != np.ndarray:
            dice = self.dice
        else:
            self.log[self.round, 2].append(dice)

        # Calculate score.
        score = 0  # 0 if not applicable
        check = CATEGORIES_CHECK[category]
        if check(dice):
            scoring = CATEGORIES_SCORING[category]
            score = scoring(dice)
        
        # Write in the score.
        self.scoresheet[category] = score
        self.log[self.round, 0] = CATEGORIES_NAMES[category]
        self.log[self.round, 1] = score

        # Check for Bonus category.
        segment = self.scoresheet[0:NUM_UPPER]
        upper_score = np.sum(segment[segment != EMPTY])
        if upper_score >= BONUS_THRESHOLD and self.log[NUM_CATEGORIES-1, 2] == None:
            self.scoresheet[NUM_CATEGORIES-1] = CATEGORIES_SCORING[NUM_CATEGORIES-1](self.dice)
            self.log[NUM_CATEGORIES-1, 0] = CATEGORIES_NAMES[NUM_CATEGORIES-1]
            self.log[NUM_CATEGORIES-1, 1] = CATEGORIES_SCORING[NUM_CATEGORIES-1](self.dice)
            self.log[NUM_CATEGORIES-1, 2] = self.round

        # Set up for next round.
        self.round += 1
        self.rerolls = MAX_REROLLS
        if self.round >= NUM_CATEGORIES - 1:
            return self.calculate_score()
        else:
            # Rerolls the next round dice (not a choice).
            self.roll_dice(np.array([False, False, False, False, False]))
            return 0


    def undo_round(self):
        """
        Undo what has been done for the previous round.
        Round and reroll counts are reset, dice is reset to the initial roll for the round.
        Log is also cleared.
        Throws an exception if there are no rounds to undo (round 0).
        """
        # Collecting info for round undo operation.
        prev_round = self.round - 1
        if prev_round < 0:
            raise Exception("No rounds left to undo.")
        prev_write = CATEGORIES_NAMES.index(self.log[prev_round, 0])
        prev_rolls = self.log[prev_round, 2]
        initial_roll = prev_rolls[0]
        bonus_round = self.log[NUM_CATEGORIES - 1, 2]

        # Undo round.
        self.round -= 1
        self.rerolls = MAX_REROLLS - 1
        self.dice = initial_roll
        self.scoresheet[prev_write] = EMPTY
        self.log[prev_round] = [None, None, None]
        if bonus_round == prev_round:  # if bonus was also achieved previous round
            self.scoresheet[NUM_CATEGORIES - 1] = 0
            self.log[NUM_CATEGORIES - 1] = [None, None, None]


    def calculate_score(self):
        """
        Calculates total score of the current score sheet.
        """
        total_score = np.sum(self.scoresheet[self.scoresheet[:] != 255])
        #total_score += self.get_bonus()
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

CATEGORY_NAME2ID = {
    'Ones': 0,
    'Twos': 1,
    'Threes': 2,
    'Fours': 3,
    'Fives': 4,
    'Sixes': 5,
    'Three-of-a-Kind': 6,
    'Four-of-a-Kind': 7,
    'Full House': 8,
    'Small Straight': 9,
    'Large Straight': 10,
    'Yahtzee': 11,
    'Chance': 12,
    'Bonus': 13,
}

CATEGORIES_SCORING = [
    lambda dice: np.count_nonzero(dice == 1),
    lambda dice: np.count_nonzero(dice == 2) * 2,
    lambda dice: np.count_nonzero(dice == 3) * 3,
    lambda dice: np.count_nonzero(dice == 4) * 4,
    lambda dice: np.count_nonzero(dice == 5) * 5,
    lambda dice: np.count_nonzero(dice == 6) * 6,
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
    lambda dice: max([np.count_nonzero(dice == die) for die in set(dice)]) >= 3,
    lambda dice: max([np.count_nonzero(dice == die) for die in set(dice)]) >= 4,
    lambda dice: (max([np.count_nonzero(dice == die) for die in set(dice)]) == 3 and 
                  min([np.count_nonzero(dice == die) for die in set(dice)]) == 2),
    lambda dice: (len(set(dice).intersection({1, 2, 3, 4})) == 4 or 
                  len(set(dice).intersection({2, 3, 4, 5})) == 4 or
                  len(set(dice).intersection({3, 4, 5, 6})) == 4),
    lambda dice: set(dice) in ({1, 2, 3, 4, 5}, {2, 3, 4, 5, 6}),
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
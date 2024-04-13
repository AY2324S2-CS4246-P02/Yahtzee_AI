import importlib
import sys
import os

module_path = os.path.join(os.path.dirname(__file__), '..')

if module_path not in sys.path:
    sys.path.append(module_path)

imported_modules = [
    importlib.import_module("Agent.Yahtzee")
]
for imported_module in imported_modules:
    importlib.reload(imported_module)

import unittest
import numpy as np
from Agent import Yahtzee

game = Yahtzee.Yahtzee()
base = np.array([1, 2, 3, 4, 5])
game.dice = base

class TestScoreCalculation(unittest.TestCase):

    def test_counts(self):
        for die in range(1, 7):
            game.reset()
            game.dice = base
            for count in range(1, 6):
                game.dice[count - 1] = die
            self.assertEqual(game.getScore(die - 1),
                             die * count,
                             f'{count} of {die} dice should be {count * die}')

    def test_bonus_borderline(self):
        game.reset()
        game.write_score(0, np.array([1, 1, 1, 2, 2])) # 3
        game.write_score(1, np.array([2, 2, 2, 1, 1])) # 6
        game.write_score(2, np.array([3, 3, 3, 2, 2])) # 9
        game.write_score(3, np.array([4, 4, 4, 2, 2])) # 12
        game.write_score(4, np.array([5, 5, 5, 2, 2])) # 15
        game.write_score(5, np.array([6, 6, 6, 2, 2])) # 18
        # total should be 63 -> bonus
        for die in range(1, 7):
            self.assertEqual(game.scoresheet[die - 1],
                             die * 3,
                             f'{3} of {die} dice should be {3 * die}')
        self.assertEqual(game.scoresheet[13],
                         35,
                         f'Bonus should be {35}')
        self.assertEqual(game.calculate_score(), 35+63,
                         f'Total should be {35+63}')

    def test_bonus_above(self):
        game.reset()
        game.write_score(0, np.array([1, 1, 1, 2, 2])) # 3
        game.write_score(1, np.array([2, 2, 2, 1, 1])) # 6
        game.write_score(2, np.array([3, 3, 3, 3, 2])) # 12
        game.write_score(3, np.array([4, 4, 4, 2, 2])) # 12
        game.write_score(4, np.array([5, 5, 5, 2, 2])) # 15
        game.write_score(5, np.array([6, 6, 6, 2, 2])) # 18
        # total should be 66 -> bonus
        for die in range(1, 7):
            self.assertEqual(game.scoresheet[die - 1],
                             die * 3 if die != 3 else die * 4,
                             f'{3} of {die} dice should be {3 * die}')
        self.assertEqual(game.scoresheet[13],
                         35,
                         f'Bonus should be {35}')
        self.assertEqual(game.calculate_score(), 35+66,
                         f'Total should be {35+66}')
        
    def test_bonus_below(self):
        game.reset()
        game.write_score(0, np.array([1, 1, 1, 2, 2])) # 3
        game.write_score(1, np.array([2, 2, 2, 1, 1])) # 6
        game.write_score(2, np.array([3, 3, 2, 2, 2])) # 6
        game.write_score(3, np.array([4, 4, 4, 2, 2])) # 12
        game.write_score(4, np.array([5, 5, 5, 2, 2])) # 15
        game.write_score(5, np.array([6, 6, 6, 2, 2])) # 18
        # total should be 60 -> no bonus
        for die in range(1, 7):
            self.assertEqual(game.scoresheet[die - 1],
                             die * 3 if die != 3 else die * 2,
                             f'{3} of {die} dice should be {3 * die}')
        self.assertEqual(game.scoresheet[13],
                         255,
                         f'Bonus should be 255 (MAX to denote no bonus)')
        self.assertEqual(game.calculate_score(), 60,
                         f'Total should be {60}')

    def test_undo(self):
        game.reset()
        history = []
        for category in range(11):
            game.doAction(['KEEP', category])
            history.append(game.calculate_score())
        
        for turn in range(10, -1, -1):
            self.assertEqual(history[turn], game.calculate_score())
            game.undo_round()

    def test_bonus_undo(self):
        game.reset()
        history = []
        moves = [
            np.array([1, 1, 1, 1, 1]),
            np.array([2, 2, 2, 2, 2]),
            np.array([3, 3, 3, 3, 3]),
            np.array([4, 4, 4, 4, 4]),
            np.array([5, 5, 5, 5, 5]),
            np.array([6, 6, 6, 6, 6]),
        ]
        for category, move in enumerate(moves):
            game.dice = move
            game.doAction(['KEEP', category])
            history.append(game.calculate_score())
        
        for turn in range(5, -1, -1):
            self.assertEqual(history[turn], game.calculate_score())
            game.undo_round()

if __name__ == '__main__':
    unittest.main()
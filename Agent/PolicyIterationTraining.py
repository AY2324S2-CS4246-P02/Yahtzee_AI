import numpy as np
from itertools import combinations_with_replacement, product
from copy import deepcopy

import Yahtzee_7

dice_combinations = list(combinations_with_replacement(range(1, 7), 5))
num_of_combinations = len(dice_combinations)  # 252

id_to_combination = {}
combination_to_id = {}
for id in range(num_of_combinations):
    id_to_combination[id] = dice_combinations[id]
    combination_to_id[dice_combinations[id]] = id

num_of_selections = 32
selections = []
for i in range(1, 32):
    select_combination = (i >> 4, i >> 3 & 1, i >> 2 & 1, i >> 1 & 1, i & 1)
    selections.append(select_combination)
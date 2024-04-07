import numpy as np
from itertools import combinations_with_replacement, product
from copy import deepcopy

import Yahtzee_7

category_names = ["Three-of-a-Kind", "Four-of-a-Kind", "Full House",
                  "Small Straight", "Large Straight", "Yahtzee", "Chance"]
num_of_selections = 32
num_of_actions = 38
num_of_combinations = 252

class PolicyIterationAgent():

    def __init__(self):
        self.game = Yahtzee_7.Yahtzee()
        with open('policy.npy', 'rb') as f:
            self.policy = np.load(f, allow_pickle=True)
        f.close()
        dice_combinations = list(combinations_with_replacement(range(1, 7), 5))
        num_of_combinations = len(dice_combinations)  # 252

        # Translator for dice combination and id.
        self.id_to_combination = {}
        self.combination_to_id = {}
        for id in range(num_of_combinations):
            self.id_to_combination[id] = dice_combinations[id]
            self.combination_to_id[dice_combinations[id]] = id

        # Translator for action to id.
        self.selections = []
        for i in range(1, 32):
            select_combination = (i >> 4, i >> 3 & 1, i >> 2 & 1, i >> 1 & 1, i & 1)
            self.selections.append(select_combination)

        self.id_to_action = {}
        self.action_to_id = {}
        for id in range(31):
            self.id_to_action[id] = self.selections[id]
            self.action_to_id[self.selections[id]] = id
        for id in range(7):
            self.id_to_action[id + 31] = category_names[id]
            self.action_to_id[category_names[id]] = id + 31

        # Translator for scoreboard to id.
        category_combinations = []
        for i in range(128):
            category = []
            for j in reversed(range(7)):
                category.append(i >> j & 1)
            category_combinations.append(category)
        
        self.id_to_category = {}
        self.category_to_id = {}
        for id in range(128):
            self.id_to_category[id] = category_combinations[id]
            self.category_to_id[tuple(category_combinations[id])] = id
    
    def get_action(self, state_id):
        action_id = self.policy[state_id]
        if action_id in range(31):  # if reroll action
            chosen_indices = list(self.selections[action_id])
            # However, the indices are for sorted dice. Find proper indices.
            curr_dice = self.game.get_dice()
            sorted_index = np.argsort(curr_dice)
            indices = [True, True, True, True, True]
            for i in range(len(chosen_indices)):
                if chosen_indices[i] == 1:
                    indices[sorted_index[i]] = False
            return 'REROLL', tuple(indices)
        else:  # if writing to category
            category = action_id - 31
            return 'WRITE', category


    def get_curr_state_id(self):
        rerolls_left = self.game.get_rerolls()  # integer
        categories = self.game.get_scoresheet()  # np.array
        # Turning it to binary form.
        categories = np.where(categories == Yahtzee_7.EMPTY, 0, 1)
        dice_combination = sorted(self.game.get_dice())  # np.array

        category_id = self.category_to_id[tuple(categories)]
        dice_id = self.combination_to_id[tuple(dice_combination)]

        id = rerolls_left * 32256 + category_id * 252 + dice_id
        # print(rerolls_left, category_id, dice_id)
        return id

    def play_game(self):
        terminal_state = False
        while not terminal_state:
            curr_state = self.get_curr_state_id()
            action = self.get_action(curr_state)

            if action[0] == 'REROLL':
                # print(action[1])
                self.game.roll_dice(action[1])
            else:
                chosen_category = action[1]
                self.game.write_score(chosen_category)
            
            categories_left = self.game.get_available_categories()
            if len(categories_left) == 0:  # no more categories to write
                terminal_state = True
        
        # print("Game Ended!")
        # print("Score: ", self.game.calculate_score())
        # print("Log:")
        # print(self.game.log)
    
    def reset_game(self):
        self.game = Yahtzee_7.Yahtzee()
        

if __name__ == "__main__":
    agent = PolicyIterationAgent()
    scores = []
    for i in range(100):
        agent.play_game()
        score = agent.game.calculate_score()
        scores.append(score)
        agent.reset_game()
    print("Max: ", np.max(scores))
    print("Mean: ", np.mean(scores))
    agent.play_game()
    print("Example log:")
    print(agent.game.log)
from Agent import Agent
from Yahtzee import Yahtzee
import itertools
from pprint import pprint
import random


# class PolicyIterationAgent(Agent):
#     def __init__(self, yahtzee : Yahtzee, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.yahtzee = yahtzee

#     def get_agent_name(self):
#         return "Policy Iteration Agent"
    
## Reduced_state should be a tuple of (score_table (2^13 values) , unordered_dice_rolls (252 values), n_rerolls_left)
## Total of 6.2M reduced states

def generate_state_space():
    dice_values = list(itertools.combinations_with_replacement((1,2,3,4,5,6), 5))
    # for i in dice_values:
    #     print(i)

    # print(len(dice_values))

    table_states = list(itertools.product((0,1), repeat = 13))
    # print(table_states)
    # print(len(table_states))

    states = list(itertools.product(dice_values, table_states, (2,1,0)))
    # print(len(states))
    # print(states[-1])

    return states


## Given a unordered dice state, generate all possible rerolls
def generate_rerolls(dice_combination):
    assert sorted(dice_combination) == list(dice_combination)
    s = set()
    l = []
    for i in range(1, 5 + 1):
        for reroll_combination in itertools.combinations(dice_combination, i):
            if reroll_combination not in s:
                s.add(reroll_combination)
                yield reroll_combination
    
# print(generate_rerolls((1, 5, 5, 5, 6)))

def get_reroll_probabilities(dice_combination, dice_to_reroll):
    kept_dice = list(dice_combination)
    for die in dice_to_reroll:
        kept_dice.remove(die)
    kept_dice = tuple(kept_dice)
    
    num_dice_to_reroll = len(dice_to_reroll)
    reroll_results = itertools.product((1,2,3,4,5,6), repeat = num_dice_to_reroll)
    
    transition_counts = dict()
    for result in reroll_results:
        new_dice_combination = kept_dice + result
        new_dice_combination = tuple(sorted(new_dice_combination))

        if new_dice_combination not in transition_counts:
            transition_counts[new_dice_combination] = 1
        else:
            transition_counts[new_dice_combination] += 1
    
    total_num_outcomes = 6 ** num_dice_to_reroll
    for k in transition_counts:
        transition_counts[k] = transition_counts[k] / total_num_outcomes
    
    return transition_counts
# pprint(get_reroll_probabilities((1, 2, 2, 2, 2), (1, 2, 2, 2)), sort_dicts = False)

def get_reroll_all_dice_probabilities():
    return get_reroll_probabilities((1,1,1,1,1), (1,1,1,1,1))


# print(generate_state_space())
def generate_actions(state):
    ## Actions come in the format (int, tuple)
    ## If action[0] == 0, that is a reroll option. action[1] will be a tuple containing the face values of dice to reroll, generated using generate_rerolls
    ## If action[0] == 1, that is a keep action. action[1] will be a tuple with only 1 value, the (0-based) index of the column to assign to
    
    dice_values, score_table, n_rerolls_left = state

    actions = []
    if n_rerolls_left > 0:
        possible_rerolls = generate_rerolls(dice_values)

        for i in possible_rerolls:
            yield (0, i)
    
    for idx, is_filled in enumerate(score_table):
        if is_filled == 0:
            yield (1, (idx, ))

# for a in generate_actions(((1,3,3,4,5), (0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0), 1)):
#     print(a)

def get_transition_probabilities(state, action):
    ## Takes in a state and an action
    ## Returns a dict mapping next_state : probability IF the action was taken
    dice_values, score_table, n_rerolls_left = state
    is_keep, info = action

    next_state_dict = {}
    if is_keep:
        index_to_assign ,= info
        l = list(score_table)
        l[index_to_assign] = 1
        new_table = tuple(l)
        new_n_rerolls_left = 2

        dice_probabilities = get_reroll_all_dice_probabilities()

        for dice_state, prob in dice_probabilities.items():
            next_state = (dice_state, new_table, new_n_rerolls_left)
            next_state_dict[next_state] = prob
    
    elif not is_keep:
        dice_probabilities = get_reroll_probabilities(dice_values, info)

        for dice_state, prob in dice_probabilities.items():
            next_state = (dice_state, score_table, n_rerolls_left - 1)
            next_state_dict[next_state] = prob
    
    return next_state_dict

RUN_TEST = True
if (RUN_TEST == True):
    example_state = ((1, 3, 3, 5, 5), (0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1), 2)
    
    example_action = (1, (0, ))

    pprint(get_transition_probabilities(example_state, example_action))

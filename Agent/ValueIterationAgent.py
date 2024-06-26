from Agent import Agent
from Yahtzee import Yahtzee
import Yahtzee
import itertools
from pprint import pprint
import random
from functools import cache
import time
import numpy as np


class ValueIterationAgent(Agent):    
    def __init__(self, yahtzee : Yahtzee, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.yahtzee = yahtzee

    def get_agent_name(self):
        return "Value Iteration Agent"
    
    def run_value_iteration(self, max_allowable_error, save_to_file = False):
        start_time = time.perf_counter()
        n_iters = 0
        try:
            self.value_table = {
                state : 0 for state in generate_state_space()
            }
            self.max_allowable_error = max_allowable_error

            delta = self.max_allowable_error + 1
            itr = 1
            while delta > self.max_allowable_error:
                print(f"Iteration {itr}")
                itr += 1
                for s in self.value_table.keys():
                    # print(f"State = {s}")
                    n_iters += 1
                    curr_state_value = self.value_table[s]
                    
                    actions = generate_actions(s)
                    q_values = []
                    for action in actions:
                        action_q_value = sum((prob * (get_reward(s, action) + self.value_table[next_state]) for next_state, prob in get_transition_probabilities(s, action).items()))
                        q_values.append(action_q_value)
                    
                    new_state_value = max(q_values) if q_values != [] else 0
                    self.value_table[s] = new_state_value
                    delta = max(delta, abs(curr_state_value - new_state_value))
                print(f"{delta = }")
                print("----------------------")
        except KeyboardInterrupt:
            print(f"States processed =  {n_iters}")
        except BaseException:
            print("Exception thrown")
        finally:
            end_time = time.perf_counter()
            print(f"Time taken = {end_time - start_time}")

            print("Value iteration done")
            
            if save_to_file:
                with open('value_table.txt', 'w') as output:
                    pprint(self.value_table, sort_dicts= False, stream=output)
    
    def get_action(self, *args):
        raise NotImplemented

    def get_action_from_state(self, state):
        try:
            from value_table import utilities
        except ImportError:
            print("Utilities not defined. Run value iteration first.")
            raise ImportError

        best_q_value = -1
        best_action = None
        for action in generate_actions(state):
            action_q_value = sum((prob * (get_reward(state, action) + utilities[next_state]) for next_state, prob in get_transition_probabilities(state, action).items()))
            if action_q_value > best_q_value:
                best_q_value = action_q_value
                best_action = action
        
        return best_action
                

## Reduced_state should be a tuple of (score_table (2^13 values) , unordered_dice_rolls (252 values), n_rerolls_left)

def generate_state_space():
    dice_values = list(itertools.combinations_with_replacement((1,2,3,4,5,6), 5))
    # for i in dice_values:
    #     print(i)

    # print(len(dice_values))

    table_states = list(itertools.product((0,1), repeat = 7))
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

@cache
def get_reroll_all_dice_probabilities():
    return get_reroll_probabilities((1,1,1,1,1), (1,1,1,1,1))


# print(generate_state_space())
def generate_actions(state):
    ## Actions come in the format (int, tuple)
    ## If action[0] == 0, that is a reroll option. action[1] will be a tuple containing the face values of dice to reroll, generated using generate_rerolls
    ## If action[0] == 1, that is a keep action. action[1] will be a tuple with only 1 value, the (0-based) index of the column to assign to
    
    dice_values, score_table, n_rerolls_left = state

    if set(score_table) == {1}:
        return

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


def get_reward(state, action):
    ## Takes in a state and an action
    ## Returns an int, representing the reward of taking that action at that state
    dice_values, score_table, n_rerolls_left = state
    is_keep, info = action

    if not is_keep:
        return 0
    else:
        index_to_assign ,= info
        assert score_table[index_to_assign] == 0

        match index_to_assign:
            case 0: ##Three of a kind
                for v in dice_values:
                    if dice_values.count(v) >= 3:
                        return sum(dice_values)
                return 0
            case 1: ##Four of a kind
                for v in dice_values:
                    if dice_values.count(v) >= 3:
                        return sum(dice_values)
                return 0
            case 2: ##Full house
                twos_satisfied = False
                threes_satisfied = False
                for roll in set(dice_values):
                    if dice_values.count(roll) == 2:
                        twos_satisfied = True
                    elif dice_values.count(roll) == 3:
                        threes_satisfied = True
                if twos_satisfied and threes_satisfied:
                    return 25
                return 0
            case 3: ## Small straight
                if (len(set(dice_values).intersection({1, 2, 3, 4})) == 4 or 
                  len(set(dice_values).intersection({2, 3, 4, 5})) == 4 or
                  len(set(dice_values).intersection({3, 4, 5, 6})) == 4):
                    return 30
                else:
                    return 0
            case 4: ##Large straight
                if set(dice_values) in ({1, 2, 3, 4, 5}, {2, 3, 4, 5, 6}):
                    return 40
                else:
                    return 0
            case 5: ## Yahtzee
                if len(set(dice_values)) == 1:
                    return 50
                else:
                    return 0
            case 6: 
                return sum(dice_values)
            case _:
                raise Exception("No possible reward!")

def perform_action(state, action):
    transition_probabilities = get_transition_probabilities(state, action)
    return random.choices(list(transition_probabilities.keys()), weights=list(transition_probabilities.values()))



## Seed: "CS4246", total_reward = 165

RUN_TEST = True
if (RUN_TEST == True):
    agent = ValueIterationAgent(Yahtzee.Yahtzee())
    # agent.run_value_iteration(1, save_to_file=False)
    # print(get_reroll_all_dice_probabilities())
    rewards = []
    for _ in range(100):
        dices = random.choices(list(get_reroll_all_dice_probabilities().keys()), weights=list(get_reroll_all_dice_probabilities().values()))[0]
        state = (dices, (0,0,0,0,0,0,0), 2)
        total_reward = 0
        while True:
            action = agent.get_action_from_state(state)
            if action == None:
                break
            total_reward += get_reward(state, action)
            print(f"{state = }")
            print(f"{action = }")
            print(f"{total_reward = }")
            print("-------------------------")
            state = perform_action(state, action)[0]
        rewards.append(total_reward)

    rewards = np.array(rewards)
    print(f"Max: {np.max(rewards)}" )
    print(f"Mean: {np.sum(rewards) / len(rewards)}")
    print(f"Min: {np.min(rewards)}")
    print(f"Std Dev: {np.std(rewards)}")







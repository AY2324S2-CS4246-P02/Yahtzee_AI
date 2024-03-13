from Yahtzee import Yahtzee, CATEGORIES_NAMES
from qlearningAgents import QLearningAgent
from typing import List, Literal, Union, Tuple
from itertools import product

all_rewards = [0]
all_scoreboards = []

# State: Tuple(dice: list, rerolls: int, available_categories: list)
def actionFn(state) -> Tuple[Literal['REROLL', 'KEEP'], Union[List[bool], int]]:
    legalActions = []
    # If there are no more available_categories, then game has ended
    if (len(state[2]) == 0):
      return legalActions
    
    # If have more than 0 rerolls, we gain access to REROLL action
    if state[1] > 0:
      # We have 2^6 possible actions
      for permutation in list(product([True, False], repeat=6)):
        legalActions.append(("REROLL", permutation))
            
    # KEEP action has to choose a category
    for category in state[2]:
      legalActions.append(("KEEP", category))
    return legalActions

# Run one instance of Yahtzee
def runEpisode(agent: QLearningAgent, environment: Yahtzee, discount, episode, verbose=0):
    totalDiscount = 1.0
    environment.reset()
    returns = 0
    if 'startEpisode' in dir(agent): agent.startEpisode()
    if verbose > 1:
        print("BEGINNING EPISODE: "+str(episode)+"\n")
    while True:
        # DISPLAY CURRENT STATE
        state = environment.getCurrentState()
        if verbose > 1:
            print("Current State:", state)

        # END IF IN A TERMINAL STATE
        actions = actionFn(state)
        if len(actions) == 0:
            if returns > all_rewards[-1]:
                all_scoreboards.append(environment.get_scoresheet())
                all_rewards.append(returns)
            if verbose > 1:
                print("EPISODE "+str(episode)+" COMPLETE: RETURN WAS "+str(returns)+"\n")
            return returns

        # GET ACTION (USUALLY FROM AGENT)
        action = agent.get_action(state)
        if action == None:
            raise Exception('Error: Agent returned None action')

        # EXECUTE ACTION
        nextState, reward = environment.doAction(action)
        if verbose > 1:
            print("Started in state: "+str(state)+
                    "\nTook action: "+ str(action[0]), str(action[1]) if isinstance(action[1], tuple) else CATEGORIES_NAMES[action[1]]+
                    "\nEnded in state: "+str(nextState)+
                    "\nGot reward: "+str(reward)+"\n")
        # UPDATE LEARNER
        if 'observeTransition' in dir(agent):
            agent.observeTransition(state, action, nextState, reward)

        returns += reward * totalDiscount
        totalDiscount *= discount
        
from tqdm import tqdm
def train_Yahtzee(episodes = 10, lr=0.5, eps=0.3, discount=1):
    qLearnOpts = {
      'actionFn': actionFn,
      'gamma': discount,
      'alpha': lr,
      'epsilon': eps
    }
    agent = QLearningAgent(**qLearnOpts)
    env = Yahtzee()
    # RUN EPISODES
    if episodes > 0:
        print()
        print("RUNNING", episodes, "EPISODES")
        print()
    returns = 0
    for episode in tqdm(range(1, episodes+1), desc="Training", unit="Episode"):
        returns += runEpisode(agent, env, discount, episode)
    if episodes > 0:
        print()
        print("AVERAGE RETURNS FROM START STATE: "+str((returns+0.0) / episodes))
        print()
        print()

    # DISPLAY POST-LEARNING VALUES / Q-VALUES
    import json
    if agent.get_agent_name() == 'Q-Learning Agent':
        print("Q-VALUES AFTER "+str(episodes)+" EPISODES")
        # sortedQValues = sorted(agent.qValues.items(), key=lambda x: x[1], reverse=True)[:10]
        # for qValue in sortedQValues:
        #   cats = [CATEGORIES_NAMES[int(x)] for x in qValue[0][0][2]]
        #   print(f"State: Dice Values: {qValue[0][0][0]}, Rerolls: {qValue[0][0][1]}, Available Categories: {cats}, Action: {qValue[0][1][0]}, {CATEGORIES_NAMES[int(qValue[0][1][1])]} \nValue: {qValue[1]}")
        print(len(agent.qValues))
        
        with open("scores.txt", 'w') as f:
            for id, reward in enumerate(all_rewards[1:]):
                f.write(f"{reward}, {all_scoreboards[id]}\n")
        print("VALUES AFTER "+str(episodes)+" EPISODES")

import time
start_time = time.time()
train_Yahtzee(100000, lr=0.5)
print("Time Taken:", time.time() - start_time)
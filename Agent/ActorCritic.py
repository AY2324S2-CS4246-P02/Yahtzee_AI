import argparse
import numpy as np
from itertools import count
from collections import namedtuple
from itertools import product
from collections import defaultdict

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import Categorical

from Yahtzee_7 import Yahtzee
import Features
gamma = 0.99
seed = 543
log_interval = 100

env = Yahtzee()
# env.reset(seed=args.seed)
torch.manual_seed(seed)
torch.autograd.set_detect_anomaly(True)

SavedAction = namedtuple('SavedAction', ['log_prob', 'value'])

actions = []
for permutation in list(product([True, False], repeat=len(env.get_dice()))):
   actions.append(("REROLL", permutation))

for category in Features.MASTER_CATEGORIES:
    actions.append(("KEEP", category))

category2id = defaultdict()
for id, cat in enumerate(Features.MASTER_CATEGORIES):
  category2id[cat] = id

class Policy(nn.Module):
    """
    implements both actor and critic in one model
    """
    def __init__(self):
        super(Policy, self).__init__()
        self.linear = nn.Linear(len(Features.TOTAL_COMBINED_FEATURES), 128)

        # actor's layer
        self.action_head = nn.Linear(128, len(actions))

        # critic's layer
        self.value_head = nn.Linear(128, 1)

        # action & reward buffer
        self.saved_actions = []
        self.rewards = []

    def forward(self, x):
        """
        forward of both actor and critic
        """
        x = F.relu(self.linear(x))

        # actor: choses action to take from state s_t
        # by returning probability of each action

        probs = self.action_head(x)
        if env.get_rerolls() == 0:
            for i in range(2**len(env.get_dice())):
                probs[i] = -100000000000000

        for idx in range(len(Features.MASTER_CATEGORIES)):
            if idx not in env.get_available_categories():
                probs[idx + 2**len(env.get_dice())] = -100000000000000

        # critic: evaluates being in the state s_t
        action_prob = F.softmax(probs, dim=-1)
        state_values = self.value_head(x)

        # return values for both actor and critic as a tuple of 2 values:
        # 1. a list with the probability of each action over the action space
        # 2. the value from state s_t
        return action_prob, state_values


model = Policy()
optimizer = optim.Adam(model.parameters(), lr=3e-2)
eps = np.finfo(np.float32).eps.item()

def getAction(state):
    # Convert state tuple into features
    features = np.array(list(Features.getFeatures(state).values()))
    state = torch.from_numpy(features).float()
    probs, state_value = model(state)

    # create a categorical distribution over the list of probabilities of actions
    m = Categorical(probs)
    action = m.sample()
    model.saved_actions.append(SavedAction(m.log_prob(action), state_value))
    act = actions[action.item()]
    if action.item() >= 2**len(env.get_dice()):
      act = ("KEEP", category2id[act[1]])
    # print("Action taken:", act)
    return act

def finish_episode():
    """
    Training code. Calculates actor and critic loss and performs backprop.
    """
    R = 0
    saved_actions = model.saved_actions
    policy_losses = [] # list to save actor (policy) loss
    value_losses = [] # list to save critic (value) loss
    returns = [] # list to save the true values

    # calculate the true value using rewards returned from the environment
    for r in model.rewards[::-1]:
        # calculate the discounted value
        R = r + gamma * R
        returns.insert(0, R)

    returns = torch.tensor(returns)
    returns = (returns - returns.mean()) / (returns.std() + eps)

    for (log_prob, value), R in zip(saved_actions, returns):
        advantage = R - value.item()

        # calculate actor (policy) loss
        policy_losses.append(-log_prob * advantage)

        # calculate critic (value) loss using L1 smooth loss
        value_losses.append(F.smooth_l1_loss(value, torch.tensor([R])))

    # reset gradients
    optimizer.zero_grad()

    # sum up all the values of policy_losses and value_losses
    loss = torch.stack(policy_losses).sum() + torch.stack(value_losses).sum()

    # perform backprop
    loss.backward()
    optimizer.step()

    # reset rewards and action buffer
    del model.rewards[:]
    del model.saved_actions[:]

def main():
    running_reward = 10

    # run infinitely many episodes
    # for i_episode in count(1):
    for i_episode in range(5000):
        # reset environment and episode reward
        env.reset()
        ep_reward = 0

        # Run one whole game
        while True:
            state = env.getCurrentState()
            # select action from policy
            action = getAction(state)

            # take the action
            # print(action)
            nextState, reward, done = env.doAction(action)
            # print("Started in state: "+str(state)+
            #         "\nTook action: "+ str(action[0]), str(action[1]) if isinstance(action[1], tuple) else Features.MASTER_CATEGORIES[action[1]]+
            #         "\nEnded in state: "+str(nextState)+
            #         "\nGot reward: "+str(reward)+"\n")

            model.rewards.append(reward)
            ep_reward += reward

            if done: break

        # update cumulative reward
        running_reward = 0.05 * ep_reward + (1 - 0.05) * running_reward

        # perform backprop
        finish_episode()

        # log results
        if i_episode % log_interval == 0:
            print('Episode {}\tLast reward: {:.2f}\tAverage reward: {:.2f}'.format(i_episode, ep_reward, running_reward))


if __name__ == '__main__':
    main()
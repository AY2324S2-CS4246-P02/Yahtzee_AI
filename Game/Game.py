from random import choice
from Agent import Agent
from typing import List

CATEGORIES_NAMES = [
    'Ones',
    'Twos',
    'Threes',
    'Fours',
    'Fives',
    'Sixes',
    'Bonus',
    'Three-of-a-Kind',
    'Four-of-a-Kind',
    'Full House',
    'Small Straight',
    'Large Straight',
    'Yahtzee',
    'Chance'
]

CATEGORIES_SCORING = [
    lambda dice: dice.count(1),
    lambda dice: dice.count(2),
    lambda dice: dice.count(3),
    lambda dice: dice.count(4),
    lambda dice: dice.count(5),
    lambda dice: dice.count(6),
    lambda dice: 35,
    lambda dice: sum(dice),
    lambda dice: sum(dice),
    lambda dice: 25,
    lambda dice: 30,
    lambda dice: 40,
    lambda dice: 50,
    lambda dice: sum(dice)
]

CATEGORIES_CHECK = [
    lambda dice: True,
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
    lambda dice: True
]

CATEGORIES = dict(
    [(name, (score, check)) for name, score, check in zip(
        CATEGORIES_NAMES,
        CATEGORIES_SCORING,
        CATEGORIES_CHECK
    )]
)

DIE_CHOICES = [i for i in range(1, 7)]

NUM_DICE = 5
NUM_CATEGORIES = 14
MAX_REROLLS = 2

class Game:

    def __init__(
            self,
            agents: List[Agent]
            ):
        self.agents = agents
        self.num_agents = len(agents)
        
        self.board = [[-1 for _ in range(self.num_agents)]
                          for _ in range(NUM_CATEGORIES)]
    
    def play(
            self,
            logging: bool = False
            ) -> List[List[int]]:
        
        if logging:
            print('Game Start.')

        for round in range(NUM_CATEGORIES):
            if logging:
                print(f'Round {round + 1}.')

            for i, agent in enumerate(self.agents):
                if logging:
                    print(f'Agent {agent.get_agent_name()}\'s turn.')

                available_categories = [name for j, name in enumerate(CATEGORIES_NAMES) if self.board[j][i] == -1]
                dice = self.__roll_dice()
                rerolls = 0

                if logging:
                    print(f'Roll {rerolls + 1}: f{dice}')

                while rerolls < MAX_REROLLS:
                    agent_action = agent.get_action(
                        dice,
                        rerolls,
                        available_categories
                    )

                    if logging:
                        print(f'Agent chose: {agent_action}')

                    if agent_action[0] == 'REROLL':

                        dice_kept = agent_action[1]

                        if logging:
                            print(f'Agent chose to keep die/dice: {[i + 1 for i, keep in enumerate(dice_kept) if keep]}')

                        dice = self.__roll_dice(dice, dice_kept)
                        rerolls += 1

                        if logging:
                            print(f'Roll {rerolls + 1}: {dice}')

                        if rerolls == MAX_REROLLS:
                            agent_action = agent.get_action(
                                dice,
                                rerolls,
                                available_categories
                            )
                    else:
                        break
                
                agent_choice = agent_action[1]
                agent_choice_idx = CATEGORIES_NAMES.index(agent_choice)
                agent_choice_score = CATEGORIES[agent_choice][0](dice) if CATEGORIES[agent_choice][1](dice) else 0
                self.board[agent_choice_idx][i] = agent_choice_score

                if logging:
                    print(f'Agent chose category: {agent_choice}')
                    print(f'Allocated points for this choice: {agent_choice_score} pts')
                    self.__print_board()

        return self.board

    def __roll_dice(
            self,
            dice: List[int] = [0 for _ in range(NUM_DICE)],
            keep: List[bool] = [False for _ in range(NUM_DICE)]
        ) -> List[int]:

        new_dice = [0 for i in range(NUM_DICE)]
        for i in range(NUM_DICE):
            if keep[i]:
                new_dice[i] = dice[i]
                continue

            new_dice[i] = choice(DIE_CHOICES)
        
        return new_dice
    
    def __print_board(
            self
        ):
        # i will update this later
        print(self.board)
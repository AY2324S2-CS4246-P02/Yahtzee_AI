from Agent import Agent
from collections import Counter
from typing import List, Tuple, Union, Literal

class GreedyAgent(Agent):

    def __init__(
            self,
            name: str = 'GreedyAgent'
        ):
        super().__init__()
        self.name = name
        self.turn = 0
        self.strategy_mapping = {
            0: lambda dice: self.__dice_count_strat(dice, 1),
            1: lambda dice: self.__dice_count_strat(dice, 2),
            2: lambda dice: self.__dice_count_strat(dice, 3),
            3: lambda dice: self.__dice_count_strat(dice, 4),
            4: lambda dice: self.__dice_count_strat(dice, 5),
            5: lambda dice: self.__dice_count_strat(dice, 6),
            6: lambda dice: self.__of_a_kind_strat(dice),
            7: lambda dice: self.__of_a_kind_strat(dice),
            8: lambda dice: self.__full_house_strat(dice),
            9: lambda dice: self.__straight_strat(dice),
            10: lambda dice: self.__straight_strat(dice),
            11: lambda dice: self.__yahtzee_strat(dice),
            12: lambda dice: self.__chance_strat(dice),
        }

    def get_agent_name(self):
        return self.name
    
    def get_action(
        self,
        dice: List[int],
        rerolls: int,
        available_categories: List[str]
    ) -> Tuple[Literal['REROLL', 'KEEP'], Union[List[bool], int]]:
        if rerolls == 0:
            action = ('KEEP', self.turn)
            self.turn += 1
            return action
        choices = self.strategy_mapping[self.turn](dice)
        return ('REROLL', choices)

    def __dice_count_strat(
            self,
            dice: List[int],
            target: int
        ):
        return [die == target for die in dice]

    def __of_a_kind_strat(
            self,
            dice: List[int]    
        ):
        counter = Counter(dice)
        target, high_count = counter.most_common(1)[0]
        if high_count == 1:
            return [False for _ in range(5)]
        return [die == target for die in dice]
    
    def __full_house_strat(
            self,
            dice: List[int]  
        ):
        counter = Counter(dice)
        if len(counter) == 2:
            if counter.most_common(1)[0][1] == 3:
                return [True for _ in range(5)]
            keep_top = 3
            choices = []
            for die in dice:
                if die == counter.most_common(1)[0][0]:
                    choices.append(keep_top == 0)
                    keep_top -= 1
                else:
                    choices.append(False)
            return choices
        elif counter.most_common(1)[0][1] == 2:
            if counter.most_common(2)[1][1] == 2:
                return [(die == counter.most_common(1)[0][0] or 
                         die == counter.most_common(2)[1][0]) for die in dice]
            else:
                return [die == counter.most_common(1)[0][0] for die in dice]
        else:
            return [False for _ in range(5)]

    def __straight_strat(
            self,
            dice: List[int]
        ):
        dice_idx = [[die, i, True] for i, die in enumerate(dice)]
        dice_idx.sort(key = lambda x: x[0])
        for i in range(1, 5):
            if dice_idx[i][0] != dice_idx[i - 1][0] + 1:
                dice_idx[i - 1][2] = False
        dice_idx.sort(key = lambda x: x[1])
        return [die[2] for die in dice_idx]

    def __yahtzee_strat(
            self,
            dice: List[int]
        ):
        counter = Counter(dice)
        return [die == counter.most_common(1)[0][0] for die in dice]
    
    def __chance_strat(
            self,
            dice: List[int],
            threshold: int = 5    
        ):
        return [die >= threshold for die in dice]
    
if __name__ == '__main__':
    import os
    import Yahtzee
    from tqdm import tqdm
    import pandas as pd

    MAX_ITER = 10000
    history = []

    for _ in tqdm(range(MAX_ITER)):
        agent = GreedyAgent()
        final_score = agent.play_game()
        final_scoresheet = [score for score in agent.game.get_scoresheet()]
        iter_information = [final_score] + final_scoresheet
        history.append(iter_information)

    history = pd.DataFrame(history, columns = ['Score'] + Yahtzee.CATEGORIES_NAMES)
    history.to_csv(os.path.join(os.path.dirname(__file__), '..', 'results', 'greedy_agent.csv'))
    
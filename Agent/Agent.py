from abc import ABC, abstractmethod
from typing import List, Literal, Union, Tuple
from Yahtzee import CATEGORIES_NAMES
import Yahtzee

LOGGING = False

class Agent(ABC):

    def __init__(self):
        self.game = Yahtzee.Yahtzee()
        self.move_history = []

    def __category_idx_to_str(
            categories: List[int]
        ) -> List[str]:
        return list(map(lambda idx: CATEGORIES_NAMES[idx], categories))

    @abstractmethod
    def get_agent_name(
        self
        ) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_action(
        self,
        dice: List[int],
        rerolls: int,
        available_categories: List[str]
    ) -> Tuple[Literal['REROLL', 'KEEP'], Union[List[bool], int]]:
        raise NotImplementedError
    
    def play_game(self):
        for round in range(13):
            chosen_category = None
            while self.game.get_rerolls() > 0:
                action = self.get_action(
                    self.game.get_dice(),
                    self.game.get_rerolls(),
                    Agent.__category_idx_to_str(self.game.get_available_categories())
                )

                self.move_history.append((round, action, [die for die in self.game.get_dice()]))

                if action[0] == 'REROLL':
                    self.game.roll_dice(action[1])
                else:
                    chosen_category = action[1]
                    break
            if chosen_category == None:
                action = self.get_action(
                    self.game.get_dice(),
                    self.game.get_rerolls(),
                    Agent.__category_idx_to_str(self.game.get_available_categories())
                )

                self.move_history.append((round, action, [die for die in self.game.get_dice()]))

                chosen_category = action[1]

            self.game.write_score(chosen_category)

        if LOGGING:
            print("\n".join(list(map(
                lambda entry: f"Round {entry[0]}: {entry[2]} -> {entry[1][0]} -> {entry[1][1]}",
                self.move_history
            ))))
            print(f"Total score = {self.game.calculate_score()}")
            print(f"{self.game.scoresheet}")
        return self.game.calculate_score()
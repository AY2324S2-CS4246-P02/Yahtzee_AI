from typing import Tuple, List, Literal, Union
from Agent import Agent
from Yahtzee import NUM_DICE, CATEGORY_NAME2ID

class PlayByHandAgent(Agent):

    def __init__(
            self,
            agent_name: str = 'Agent'
        ):
        super().__init__()
        self.agent_name = agent_name

    def get_agent_name(self) -> str:
        return self.agent_name
    
    def get_action(
            self,
            dice: List[int],
            rerolls: int,
            available_categories: List[str]
        ) -> Tuple[Literal['REROLL', 'KEEP'], Union[List[bool], str]]:
        combined_action = []
        
        print(f"Dice received: {dice}")

        if rerolls > 0:
            action = input("Which action do you choose? [REROLL or KEEP]")
        else:
            print(f"Maximum rerolls reached. Agent must keep")
            action = 'KEEP'
        combined_action.append(action)
        
        if action == 'REROLL':
            dice_kept = input("Which dice do you want to keep? [1-5, space-separated]")
            try:
                dice_kept = list(map(int, dice_kept.split(" ")))
            except:
                dice_kept = []
            dice_kept = [i + 1 in dice_kept for i in range(NUM_DICE)]
            combined_action.append(dice_kept)
        else:
            category = input(f"Which category do you want to choose? Available Categories are:\n{available_categories}")
            combined_action.append(CATEGORY_NAME2ID[category])

        return combined_action

if __name__ == '__main__':
    agent = PlayByHandAgent()
    agent.play_game()
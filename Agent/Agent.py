from abc import ABC, abstractmethod
from typing import List, Literal, Union, Tuple

class Agent(ABC):

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
    ) -> Tuple[Literal['REROLL', 'KEEP'], Union[List[bool], str]]:
        raise NotImplementedError
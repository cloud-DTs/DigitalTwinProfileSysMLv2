from .twin_model import TwinModel

from enum import Enum
from dataclasses import dataclass


class StrategyType(Enum):
    LAMBDA = "lambda"
    CONTAINER = "container"

@dataclass
class Strategy(TwinModel):
    strategyType: StrategyType = StrategyType.LAMBDA
    pathToCode: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.get_unique_id(),
            "name": self.name,
            "strategyType": self.strategyType.value,
            "pathToCode": self.pathToCode
        }
    
   
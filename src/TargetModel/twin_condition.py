from __future__ import annotations
from typing import TYPE_CHECKING
from enum import Enum
from typing import Optional
from .twin_model import TwinModel
from .twin_measureAttribute import MeasureAttribute
from .twin_strategy import Strategy
from dataclasses import dataclass
if TYPE_CHECKING:
    from .twin import Twin
class CONDITION_OPERATOR(Enum):
    GREATER_THAN = "GREATER_THAN"
    LESS_THAN = "LESS_THAN"
    EQUAL = "EQUAL"
    GREATER_EQUAL = "GREATER_EQUAL"
    LESS_EQUAL = "LESS_EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
@dataclass
class Condition(TwinModel):
    
    leftOperand: MeasureAttribute = None
    operator: CONDITION_OPERATOR = CONDITION_OPERATOR.EQUAL
    rightOperand: MeasureAttribute = None
    twin:Twin = None
    strategy:Strategy = None

    def add_strategy(self, strategy:Strategy):
        self.strategy = strategy
    def to_dict(self) -> dict:
        return {
            "id": self.get_unique_id(),
            "name": self.name,
            "leftOperand": self.leftOperand.to_dict() if self.leftOperand else None,
            "operator": self.operator.value,
            "rightOperand": self.rightOperand.to_dict() if self.rightOperand else None,
            "strategy": self.strategy.to_dict() if self.strategy else None
        }
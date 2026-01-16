from __future__ import annotations
from typing import TYPE_CHECKING, List
from enum import Enum
from typing import Optional
from .twin_model import TwinModel
from .twin_measureAttribute import MeasureAttribute
from .twin_strategy import Strategy
from dataclasses import dataclass,field
if TYPE_CHECKING:
    from .twin import Twin
class CONDITION_OPERATOR(Enum):
    GREATER_THAN = "GREATER_THAN"
    LESS_THAN = "LESS_THAN"
    EQUAL = "EQUAL"
    GREATER_EQUAL = "GREATER_EQUAL"
    LESS_EQUAL = "LESS_EQUAL"
    NOT_EQUAL = "NOT_EQUAL"

def opToSymbol(op: CONDITION_OPERATOR) -> str:
    if op == CONDITION_OPERATOR.GREATER_THAN:
        return ">"
    elif op == CONDITION_OPERATOR.LESS_THAN:
        return "<"
    elif op == CONDITION_OPERATOR.EQUAL:
        return "=="
    elif op == CONDITION_OPERATOR.GREATER_EQUAL:
        return ">="
    elif op == CONDITION_OPERATOR.LESS_EQUAL:
        return "<="
    elif op == CONDITION_OPERATOR.NOT_EQUAL:
        return "!="
    else:
        return "unknown_operator"
@dataclass
class Condition(TwinModel):
    
    leftOperand: MeasureAttribute = None
    operator: CONDITION_OPERATOR = CONDITION_OPERATOR.EQUAL
    rightOperand: MeasureAttribute = None
    twin:Twin = None
    strategy:List[Strategy] = field(default_factory=list)

    def add_strategy(self, strategy:Strategy):
        self.strategy.append(strategy)
    def to_event_dict(self):
        
        leftOperandChain = self.getOperandChain(self.leftOperand)
        rightOperandChain = self.getOperandChain(self.rightOperand)

        res = []

        for s in self.strategy:
            newElem = {
                "condition": f"{leftOperandChain} {opToSymbol(self.operator)} {rightOperandChain}",
                "action": s.to_event_dict()
            }
            res.append(newElem)
        return res
    
    def getOperandChain(self,attribute:MeasureAttribute)->str:
        chain = [attribute.parentComponent.parentEntity.id,attribute.parentComponent.id, attribute.id]
        return ".".join(chain)
    
    
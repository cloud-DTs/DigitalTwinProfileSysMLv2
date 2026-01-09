from .twin_model import TwinModel

from enum import Enum
from dataclasses import dataclass
from typing import Optional
from .twin_component import Component
class StrategyType(Enum):
    LAMBDA = "lambda"
    CONTAINER = "container"

class FeedbackTopicType(Enum):
    EXTERN = "EXTERN"
    INTERN = "INTERN"
    NOFEEDBACK = "NOFEEDBACK"

@dataclass
class Strategy(TwinModel):
    strategyType: StrategyType = StrategyType.LAMBDA
    pathToCode: str = ""
    external:bool = False
    feedbackTopicType:FeedbackTopicType = FeedbackTopicType.NOFEEDBACK
    customPaylod:Optional[dict] = None
    componentTopic:Component = None
    externalTopic:str = ""


    def to_event_dict(self) -> dict:
        res = {
            "type": self.strategyType.value,
            "pathToCode": self.pathToCode,
            "functionName": self.name,
            "external": self.external,
            "feedback": {
                "type": "mqtt"
            }
        }
        feedback = res["feedback"]
        
        if self.componentTopic:
            feedback["componentTopic"] = {"iotDeviceId": self.componentTopic.id}
        
        if self.externalTopic:
            feedback["customTopic"] = {"topic": self.externalTopic}
            
        if self.customPaylod:
            feedback["payload"] = self.customPaylod
        else:
            feedback["payload"] = "action-result"

        return res

   
from .twin_measureAttribute import MeasureAttribute, AttributeDataType
from .twin_constAttribute import ConstAttribute
from .twin_component import Component
from .twin_model import TwinModel
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class StrategyType(Enum):
    LAMBDA = "lambda"
    CONTAINER = "container"


class FeedbackTopicType(Enum):
    EXTERN = "EXTERN"
    INTERN = "INTERN"
    NOFEEDBACK = "NOFEEDBACK"


@dataclass
class ActionOutputParameterType:
    name: str
    type: AttributeDataType


@dataclass
class ActionInputParameter:
    attribute: MeasureAttribute
    customName: str = ""

    @property
    def resolved_name(self) -> str:
        return self.customName if self.customName != "inputParameters" else self.attribute.name


@dataclass
class Strategy(TwinModel):
    strategyType: StrategyType = StrategyType.LAMBDA
    pathToCode: str = ""
    external: bool = False
    feedbackTopicType: FeedbackTopicType = FeedbackTopicType.NOFEEDBACK
    customPayload: Optional[dict] = None  # fixed typo: customPaylod -> customPayload
    componentTopic: Optional[Component] = None
    externalTopic: str = ""
    inputParameters: list[ActionInputParameter] = field(default_factory=list)
    constInputParameters: list[ConstAttribute] = field(default_factory=list)
    outputParameters: list[ActionOutputParameterType] = field(default_factory=list)

    def _build_feedback_dict(self) -> dict:
        feedback: dict = {"type": "mqtt"}
        if self.componentTopic:
            feedback["iotDeviceId"] = self.componentTopic.id
        if self.externalTopic:
            feedback["topic"] = self.externalTopic
        feedback["payload"] = self.customPayload or "action-result"
        return feedback

    def _serialize_input_parameters(self) -> list[dict]:
        result = []
        for param in self.inputParameters:
            entry = param.attribute.to_event_dict()
            entry["name"] = param.resolved_name
            entry["id"] = self.getOperandChain(param.attribute)
            result.append(entry)
        return result
    def getOperandChain(self,attribute:MeasureAttribute)->str:
        chain = [attribute.parentComponent.parentEntity.id,attribute.parentComponent.name, attribute.name]
        return ".".join(chain)
    
    def _serialize_output_parameters(self) -> list[dict]:
        return [{"name": p.name, "dataType": p.type} for p in self.outputParameters]

    def to_event_dict(self) -> dict:
        res = {
            "type": self.strategyType.value,
            "pathToCode": self.pathToCode,
            "functionName": self.name,
            "external": self.external,
        }
        if self.feedbackTopicType != FeedbackTopicType.NOFEEDBACK:
            res["feedback"] = self._build_feedback_dict()

        res["inputParameters"] = self._serialize_input_parameters()
        res["outputParameters"] = self._serialize_output_parameters()
        return res
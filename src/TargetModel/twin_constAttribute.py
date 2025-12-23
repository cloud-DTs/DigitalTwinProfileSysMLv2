from .twin_measureAttribute import MeasureAttribute,AttributeDataType
from dataclasses import dataclass
from typing import Optional

@dataclass
class ConstAttribute(MeasureAttribute):
    value: str = ""

    def to_dict(self):
        return super().to_dict() | {
            "value": self.value
        }

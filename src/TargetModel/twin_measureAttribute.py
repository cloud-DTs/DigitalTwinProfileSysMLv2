from __future__ import annotations
from typing import TYPE_CHECKING
from enum import Enum
from typing import Optional
from .twin_model import TwinModel

if TYPE_CHECKING:
    from .twin_component import Component

    
from dataclasses import dataclass
class AttributeDataType(Enum):
    STRING = "STRING"
    INTEGER = "INTEGER"
    DOUBLE = "DOUBLE"

@dataclass
class MeasureAttribute(TwinModel):
    dataType: AttributeDataType = AttributeDataType.STRING
    parentComponent: Component = None

    def to_iot_device_dict(self) -> dict:
        return {
            "name": self.name,
            "dataType": self.dataType.value
        }

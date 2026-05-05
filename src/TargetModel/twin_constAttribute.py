from .twin_measureAttribute import MeasureAttribute,AttributeDataType
from dataclasses import dataclass
from typing import Optional

@dataclass
class ConstAttribute(MeasureAttribute):
    value: str = ""

    def to_iot_device_dict(self) -> dict:
        base_dict = super().to_iot_device_dict()
        base_dict.update({
            "initValue": self.pythonTypes()(self.value)
        })
        return base_dict
    
    def to_event_dict(self) -> dict:
        base_dict = super().to_event_dict()
        base_dict.update({
            "value": self.pythonTypes()(self.value)
        })
        return base_dict


    def pythonTypes(self):
        if self.dataType == AttributeDataType.STRING:
            return str
        elif self.dataType == AttributeDataType.INTEGER:
            return int
        elif self.dataType == AttributeDataType.DOUBLE:
            return float
        else:
            return str  
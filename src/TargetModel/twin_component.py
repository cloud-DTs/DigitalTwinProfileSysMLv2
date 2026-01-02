from __future__ import annotations
from typing import TYPE_CHECKING

from dataclasses import dataclass,field
from typing import List, Optional
from .twin_model import TwinModel
from .twin_measureAttribute import MeasureAttribute
if TYPE_CHECKING:
    from .twin_entity import TwinEntity

@dataclass
class Component(TwinModel):
    attributes: List[MeasureAttribute] = field(default_factory=list)
    parentEntity: TwinEntity = None

    def add_attribute(self, attribute: MeasureAttribute):
        self.attributes.append(attribute)
        attribute.parentComponent = self
    
    def to_dict(self) -> dict:
        return {
            "id": self.get_unique_id(),
            "name": self.name,
            "attributes": [attribute.to_dict() for attribute in self.attributes]
        }
    
    def to_hierarchy_dict(self) ->dict:
        return {
            "iotDeviceId": self.id,
            "type":"component",
            "name": self.name
        }

    def to_iot_device_dict(self) -> dict:
        return {
            "id": self.id,
            "properties": [attribute.to_iot_device_dict() for attribute in self.attributes]
        }


@dataclass
class ConstComponent(Component):
    def __init__(self, entityId:str,entityName:str):
        super().__init__(entityId+"const_component", entityName+"const_component",[],None)
    
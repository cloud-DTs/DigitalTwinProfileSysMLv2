from __future__ import annotations
from typing import TYPE_CHECKING
from enum import Enum
from dataclasses import dataclass
from typing import Optional
from .twin_model import TwinModel
from .twin_database import TwinDatabase
from .twin_measureAttribute import MeasureAttribute

if TYPE_CHECKING:
    from .twin import Twin
class InterfaceType(Enum):
    MQTT = "MQTT"
    GRPC = "GRPC"
    REST = "REST"    
@dataclass
class TwinMeasurementInterface(TwinModel):
    interfaceType: InterfaceType = InterfaceType.MQTT
    attribute_endpoint: MeasureAttribute = None
    parentTwin: Twin = None
    dataBase_endpoint: TwinDatabase = None

    def to_dict(self) -> dict:
        return {
            "id": self.get_unique_id(),
            "name": self.name,
            "interfaceType": self.interfaceType.value,
            "attribute_endpoint": self.attribute_endpoint.to_dict() if self.attribute_endpoint else None,
            "dataBase_endpoint": self.dataBase_endpoint.to_dict() if self.dataBase_endpoint else None
        }

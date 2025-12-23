from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from .twin_model import TwinModel
from .twin_entity import TwinEntity
from .twin_database import TwinDatabase
from .twin_interface import TwinMeasurementInterface
from .twin_condition import Condition
@dataclass
class Twin(TwinModel):
    entities: List[TwinEntity] = field(default_factory=list)
    dataBases: List[TwinDatabase] = field(default_factory=list)
    measurementInterfaces: List[TwinMeasurementInterface] = field(default_factory=list)
    strategies: List[Condition] = field(default_factory=list)
        
    def add_entity(self, entity: TwinEntity):
        self.entities.append(entity)
        entity.twin = self

    def add_dataBase(self, dataBase: TwinDatabase):
        self.dataBases.append(dataBase)
        dataBase.parentTwin = self

    def add_measurementInterface(self, measurementInterface: TwinMeasurementInterface):
        self.measurementInterfaces.append(measurementInterface)
        measurementInterface.parentTwin = self
    def add_condition(self, condition: Condition):
        self.strategies.append(condition)
        condition.twin = self

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "entities": [entity.to_dict() for entity in self.entities],
            "dataBases": [db.to_dict() for db in self.dataBases],
            "measurementInterfaces": [mi.to_dict() for mi in self.measurementInterfaces],
            "strategies": [strategy.to_dict() for strategy in self.strategies],
        }


    
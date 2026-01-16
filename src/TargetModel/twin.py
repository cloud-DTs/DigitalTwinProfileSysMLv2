from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from .twin_model import TwinModel
from .twin_entity import TwinEntity
from .twin_database import TwinDataBaseTier, TwinDatabase

from .twin_condition import Condition
@dataclass
class Twin(TwinModel):
    entities: List[TwinEntity] = field(default_factory=list)
    hotdatabase: TwinDatabase = None
    colddatabase: TwinDatabase = None
    strategies: List[Condition] = field(default_factory=list)
        
    def add_entity(self, entity: TwinEntity):
        self.entities.append(entity)
        entity.twin = self

    def add_condition(self, condition: Condition):
        self.strategies.append(condition)
        condition.twin = self

    def to_hierarchy_dict(self) ->dict:
        return [x.to_hierarchy_dict() for x in self.entities]

    def to_iot_device_dict(self) -> dict:
        result = []
        for  entity in self.entities:
            result.extend(entity.to_iot_device_dict())
        return result

    def to_event_dict(self) -> list[dict]:
        result = []

        for condition in self.strategies:
            result.extend(condition.to_event_dict())

        return result


    def to_config_dict(self) -> dict:
        return {
            "digital_twin_name": self.name,
            "hot_storage_size_in_days": self.hotdatabase.retentionDays if self.hotdatabase else None,
            "cold_storage_size_in_days": self.colddatabase.retentionDays if self.colddatabase else None,
        }


    
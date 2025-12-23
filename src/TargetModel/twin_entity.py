from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass, field
from typing import List, Optional
from .twin_model import TwinModel
from .twin_component import Component, ConstComponent
from .twin_constAttribute import ConstAttribute
if TYPE_CHECKING:
    from .twin import Twin

@dataclass
class TwinEntity(TwinModel):
    subEntities: List['TwinEntity'] = field(default_factory=list)
    components: List[Component] = field(default_factory=list)
    constComponent: ConstComponent = None
    parentEntity: Optional[TwinEntity] = None
    twin:Twin = None

    def add_subEntity(self, entity: TwinEntity):
        self.subEntities.append(entity)
        entity.parentEntity = self
        entity.twin = self.twin
        
    def isRootEntity(self) -> bool:
        return self.parentEntity is None

    def add_component(self, component: Component):
        self.components.append(component)
        component.parentEntity = self

    def to_dict(self) -> dict:
        return {
            "id": self.get_unique_id(),
            "name": self.name,
            "subEntities": [entity.to_dict() for entity in self.subEntities],
            "components": [component.to_dict() for component in self.components],
            "constComponent": self.constComponent.to_dict() if self.constComponent else None
        }
    
    def add_constAttribute(self, constAttribute: ConstAttribute):
        if self.constComponent is None:
            self.constComponent = ConstComponent(self.id, self.name)
        self.constComponent.add_attribute(constAttribute)
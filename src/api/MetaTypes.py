from enum import Enum

class MetaTypes(Enum):
    
    Twin = "Twin"
    Entity = "Entity"
    entity = "entity"


    Component = "Component"
    component = "component"

    MeasureInterface = "MeasureInterface"
    measureInterface = "measureInterface"

    ConstAttribute = "ConstAttribute"
    constAttribute = "constAttribute"
    MeasureAttribute = "MeasureAttribute"
    measureAttribute = "measureAttribute"
  
    Condition = "Condition"
    condition = "condition"
    strategyAction = "strategyAction"

    @classmethod
    def all_meta_types(cls):
        return [meta_type.value for meta_type in cls]

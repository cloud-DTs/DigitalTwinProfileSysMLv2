from .ApiTypes import ApiTypes
from enum import Enum

class MetaTypes(Enum):
    
    Twin = "Twin"
    Entity = "Entity"
    entity = "entity"


    Component = "Component"
    component = "component"


    DataBase = "DataBase"
    database = "database"


    MeasureInterface = "MeasureInterface"
    measureInterface = "measureInterface"


    Measurement = "Measurement"
    measure = "measure"

   
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

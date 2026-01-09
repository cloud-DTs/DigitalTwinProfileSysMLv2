from typing import TypeVar, Type, Generic, List, Tuple, Optional
import uuid
from dataclasses import dataclass, field
import logging
from ..TargetModel.twin_model import TwinModel
T = TypeVar("T" ,bound=TwinModel)
MY_APP_NAMESPACE = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
@dataclass
class IdWrapper(Generic[T]):
 
    dataTable: dict[Tuple[str, ...], T] = field(default_factory=dict)

    uuidLookup: dict[str, Tuple[str, ...]] = field(default_factory=dict)

    def register(self, model: T, path_list: List[str]) -> str:
        path_tuple = tuple(path_list)
        
        if path_tuple in self.dataTable:
            return getattr(self.dataTable[path_tuple], 'id', '')

        self.dataTable[path_tuple] = model
        name_path_list = self.get_name_path_from_path_list(path_list)
        name_path_string = "/".join(name_path_list)
        
        custom_uuid = str(uuid.uuid5(MY_APP_NAMESPACE, name_path_string))
        
        logging.info(f"Generated UUID {custom_uuid} for path {name_path_string}")
        
        self.uuidLookup[custom_uuid] = path_tuple
       
        model.id = custom_uuid
            
        return custom_uuid

    def get_name_path_from_path_list(self, path_list: List[str]) -> List[str]:

        name_path = []
        current_path = []
        
        for segment in path_list:
            current_path.append(segment)
            model:TwinModel = self.get_by_path(current_path)
            name_path.append(model.name)
                
        return name_path
    
    def get_by_path(self, path_list: List[str]) -> Optional[T]:
        return self.dataTable.get(tuple(path_list))
    
    def get_db_model(self, custom_id: str) -> T:
        path_tuple = self.uuidLookup.get(custom_id)
        if path_tuple:
            return self.dataTable[path_tuple]
        else:
            raise KeyError(f"No model found for UUID {custom_id}")
    
    
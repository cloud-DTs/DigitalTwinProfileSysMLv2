from typing import TypeVar, Type, Generic, List, Tuple, Optional
import uuid
from dataclasses import dataclass, field

T = TypeVar("T")

@dataclass
class IdWrapper(Generic[T]):
 
    dataTable: dict[Tuple[str, ...], T] = field(default_factory=dict)

    uuidLookup: dict[str, Tuple[str, ...]] = field(default_factory=dict)

    def register(self, model: T, path_list: List[str]) -> str:
        path_tuple = tuple(path_list)
        
        if path_tuple in self.dataTable:
            existing_model = self.dataTable[path_tuple]
            return getattr(existing_model, 'id', '')

        custom_uuid = str(uuid.uuid4())
        
        self.dataTable[path_tuple] = model
        self.uuidLookup[custom_uuid] = path_tuple
        
        if hasattr(model, 'id'):
            model.id = custom_uuid
            
        return custom_uuid

    def get_by_path(self, path_list: List[str]) -> Optional[T]:
        return self.dataTable.get(tuple(path_list))
    
    def get_db_model(self, custom_id: str) -> T:
        path_tuple = self.uuidLookup.get(custom_id)
        if path_tuple:
            return self.dataTable[path_tuple]
        else:
            raise KeyError(f"No model found for UUID {custom_id}")
    
    
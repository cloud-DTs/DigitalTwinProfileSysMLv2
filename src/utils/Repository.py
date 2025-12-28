from enum import Enum
from typing import List, TypeVar
import uuid
from ..TargetModel.twin_model import TwinModel
from ..utils.IdDatabase import IdWrapper
T = TypeVar("T", bound=TwinModel)


class Repository:
    def __init__(self):
        self.dataBases: dict[type, IdWrapper] = {}

    def add_entry(self, model_type: type[T], model: T, path_list: List[str]) -> str:

        if model_type not in self.dataBases:
            self.dataBases[model_type] = IdWrapper[T]()
        
        return self.dataBases[model_type].register(model, path_list)

    def get_model_by_id(self, model_type: type[T], custom_id: str) -> T:
        if model_type in self.dataBases:
            return self.dataBases[model_type].get_db_model(custom_id)
        raise KeyError(f"No database found for model type {model_type}")

    def find_all_by_meta_id(self, model_type: type[T], meta_id: str) -> List[T]:
        found = []
        if model_type in self.dataBases:
            db = self.dataBases[model_type]
            for path_tuple, model in db.dataTable.items():
                if path_tuple[-1] == meta_id:
                    found.append(model)
        return found
    
    def get_database(self, model_type: type[T]) -> IdWrapper[T]:
        if model_type in self.dataBases:
            return self.dataBases[model_type]
        raise KeyError(f"No database found for model type {model_type}")
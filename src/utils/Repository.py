from enum import Enum
from typing import List, TypeVar, Dict, Type
import uuid
from ..TargetModel.twin_model import TwinModel
from ..utils.IdDatabase import IdWrapper

T = TypeVar("T", bound=TwinModel)

class Repository:
    def __init__(self):
        self.shared_id_wrapper = IdWrapper[TwinModel]()

    def add_entry(self, model_type: Type[T], model: T, path_list: List[str]) -> str:
        return self.shared_id_wrapper.register(model, path_list)

    def get_model_by_id(self, model_type: Type[T], custom_id: str) -> T:
        model = self.shared_id_wrapper.get_db_model(custom_id)
        if not isinstance(model, model_type):
            raise TypeError(f"Model with id {custom_id} is not of type {model_type}")
        return model

    def find_all_by_meta_id(self, model_type: Type[T], meta_id: str) -> List[T]:
        found = []
        for path_tuple, model in self.shared_id_wrapper.dataTable.items():
            if isinstance(model, model_type) and path_tuple[-1] == meta_id:
                found.append(model)
        return found
    
    def get_database(self, model_type: Type[T]) -> IdWrapper:
        return self.shared_id_wrapper
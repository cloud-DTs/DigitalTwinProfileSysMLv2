from __future__ import annotations
from enum import Enum
from typing import Any, Callable, Optional, Dict, List, Set, TypeVar, Type, cast
from .ApiTypes import ApiTypes 
from .Fields import Fields

class ApiElement:
    def __init__(self, data: Dict[str, Any] = None):
        self.raw_data = data if data else {}

    def get_field(self, field: Fields) -> Optional[Any]:
        field_name, expected_type, allowed_api_types = field.value
        actual_value = self.raw_data.get(field_name)
        current_api_type = self.raw_data.get(Fields.TYPE.value[0], 'UnknownType')

        if field_name not in self.raw_data:
            return [] if expected_type is list else None

        if allowed_api_types != ApiTypes.ALL.value:
            allowed_list = allowed_api_types if isinstance(allowed_api_types, list) else [allowed_api_types]
            
            if not any(t in current_api_type for t in allowed_list):
              
                raise TypeError(
                    f"Invalid Access: Field '{field_name}' is not allowed for ApiType '{current_api_type}'. "
                    f"Allowed types are: {allowed_list}. Element ID: {self.id}"
                )

        if field_name == "value":
            if not isinstance(actual_value, (str, int, float, bool)):
                raise TypeError(
                    f"Data Type Mismatch for 'value': Expected primitive, "
                    f"but got {type(actual_value)}. ID: {self.id}"
                )
        elif actual_value is not None and not isinstance(actual_value, expected_type):
            raise TypeError(
                f"Data Type Mismatch for field '{field_name}': "
                f"Expected {expected_type}, but got {type(actual_value)}. Element ID: {self.id}"
            )
            
        return actual_value

    def load_field_from_api(self, field: Fields) -> Optional[ApiElement]:
        from ..element import getElementByIdTyped
        field_data = self.get_field(field)
        
        target_id = None
        if isinstance(field_data, dict):
            target_id = field_data.get(Fields.ID.value[0])
        elif isinstance(field_data, str):
            target_id = field_data

        if target_id:
            return getElementByIdTyped(ApiElement, target_id)
        return None

    def load_list_from_api(self, field: Fields) -> List[ApiElement]:
        from ..element import getElementByIdTyped
        raw_list = self.get_field(field)
        elements = []
        if not raw_list:
            return elements
        for item in raw_list:
            t_id = item.get(Fields.ID.value[0]) if isinstance(item, dict) else item
            if t_id:
                obj = getElementByIdTyped(ApiElement, t_id)
                if obj: elements.append(obj)
        return elements

    @classmethod
    def fromDict(cls, dict_obj: Dict[str, Any]) -> ApiElement:
        return cls(data=dict_obj)

    @property
    def id(self) -> str: return self.get_field(Fields.ID)
    
    @property
    def type(self) -> str: return self.get_field(Fields.TYPE)
    
    @property
    def name(self) -> str: return self.get_field(Fields.NAME) or ""


    def find_in_hierarchy(self, cond: Callable[[ApiElement], bool], visited: Optional[Set[str]] = None) -> tuple[bool, Optional[ApiElement]]:
        if visited is None:
            visited = set()
        
        if self.id in visited:
            return False, None
        visited.add(self.id)

        if cond(self):
            return True, self

        for ref in (self.get_field(Fields.OWNEDREDEFINITION) or []):
            redef_obj = self.load_field_from_api_by_id(ref['@id'])
            if redef_obj:
                target = redef_obj.load_field_from_api(Fields.REDEFINEDFEATURE)
                if target:
                    found, result = target.find_in_hierarchy(cond, visited)
                    if found:
                        return True, result

        for ref in (self.get_field(Fields.OWNEDSUBSETTING) or []):
            subset_obj = self.load_field_from_api_by_id(ref['@id'])
            if subset_obj:
                target = subset_obj.load_field_from_api(Fields.SUBSETTEDFEATURE)
                if target:
                    found, result = target.find_in_hierarchy(cond, visited)
                    if found:
                        return True, result

        return False, None

    def load_field_from_api_by_id(self, target_id: str) -> Optional[ApiElement]:
        from ..element import getElementByIdTyped
        return getElementByIdTyped(ApiElement, target_id)
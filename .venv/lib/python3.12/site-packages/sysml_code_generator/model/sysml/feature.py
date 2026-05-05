from __future__ import annotations

from dataclasses import dataclass

from sysml_code_generator.mapper.conversions import (
    get_list_of_ids,
    get_optional_id,
    get_string,
)
from sysml_code_generator.model.sysml.sysml_entity import SysMLEntity


@dataclass
class Feature(SysMLEntity):
    owned_element_ids: list[str]

    @staticmethod
    def from_dict(data) -> Feature:
        return Feature(
            id=get_string(data, "@id"),
            type_=get_string(data, "@type"),
            owner_id=get_optional_id(data, "owner"),
            name=get_string(data, "name"),
            qualified_name=get_string(data, "qualifiedName"),
            owned_element_ids=get_list_of_ids(data, "ownedElement"),
        )

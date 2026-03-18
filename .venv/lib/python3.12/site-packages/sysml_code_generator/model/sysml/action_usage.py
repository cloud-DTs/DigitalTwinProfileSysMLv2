from __future__ import annotations

from dataclasses import dataclass

from sysml_code_generator.mapper.conversions import (
    get_list_of_ids,
    get_optional_id,
    get_string,
)
from sysml_code_generator.model.sysml.sysml_entity import SysMLEntity


@dataclass
class ActionUsage(SysMLEntity):
    action_definition_ids: list[str]  # ActionDefinitions
    is_abstract: bool
    output_ids: list[str]
    input_ids: list[str]

    @staticmethod
    def from_dict(data) -> ActionUsage:
        return ActionUsage(
            id=get_string(data, "@id"),
            type_=get_string(data, "@type"),
            owner_id=get_optional_id(data, "owner"),
            name=get_string(data, "name"),
            qualified_name=get_string(data, "qualifiedName"),
            action_definition_ids=get_list_of_ids(data, "actionDefinition"),
            is_abstract=data["isAbstract"],
            output_ids=get_list_of_ids(data, "output"),
            input_ids=get_list_of_ids(data, "input"),
        )

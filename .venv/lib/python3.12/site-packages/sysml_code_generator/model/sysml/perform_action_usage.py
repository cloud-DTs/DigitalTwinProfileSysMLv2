from __future__ import annotations

from dataclasses import dataclass

from sysml_code_generator.mapper.conversions import (
    get_bool,
    get_id,
    get_list_of_ids,
    get_optional_id,
    get_string,
)
from sysml_code_generator.model.sysml.action_usage import ActionUsage


@dataclass
class PerformActionUsage(ActionUsage):
    perform_action_usage_id: str

    @staticmethod
    def from_dict(data) -> PerformActionUsage:
        return PerformActionUsage(
            id=get_string(data, "@id"),
            type_=get_string(data, "@type"),
            owner_id=get_optional_id(data, "owner"),
            name=get_string(data, "name"),
            qualified_name=get_string(data, "qualifiedName"),
            action_definition_ids=get_list_of_ids(data, "actionDefinition"),
            is_abstract=get_bool(data, "isAbstract"),
            perform_action_usage_id=get_id(data, "performedAction"),
            output_ids=get_list_of_ids(data, "output"),
            input_ids=get_list_of_ids(data, "input"),
        )

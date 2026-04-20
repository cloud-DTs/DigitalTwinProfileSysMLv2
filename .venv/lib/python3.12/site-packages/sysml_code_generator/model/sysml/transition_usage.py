from __future__ import annotations

from dataclasses import dataclass

from sysml_code_generator.mapper.conversions import (
    get_id,
    get_list_of_ids,
    get_optional_id,
    get_string,
)
from sysml_code_generator.model.sysml.sysml_entity import SysMLEntity


@dataclass
class TransitionUsage(SysMLEntity):
    # 8.3.17.9 TransitionUsage

    source_id: str  # type ActionUsage
    target_id: str  # type ActionUsage
    guard_expression_ids: list[str]  # type Expression
    effect_action_ids: list[str]  # type ActionUsage
    trigger_action_ids: list[str]  # type AcceptActionUsage

    @staticmethod
    def from_dict(data) -> TransitionUsage:
        return TransitionUsage(
            id=get_string(data, "@id"),
            type_=get_string(data, "@type"),
            owner_id=get_optional_id(data, "owner"),
            name=get_string(data, "name"),
            qualified_name=get_string(data, "qualifiedName"),
            source_id=get_id(data, "source"),
            target_id=get_id(data, "target"),
            effect_action_ids=get_list_of_ids(data, "effectAction"),
            guard_expression_ids=get_list_of_ids(data, "guardExpression"),
            trigger_action_ids=get_list_of_ids(data, "triggerAction"),
        )

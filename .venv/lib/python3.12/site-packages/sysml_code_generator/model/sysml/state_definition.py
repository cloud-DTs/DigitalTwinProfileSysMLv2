from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sysml_code_generator.mapper.conversions import (
    get_bool,
    get_optional_id,
    get_string,
)
from sysml_code_generator.model.sysml.behavior import Behavior


@dataclass
class StateDefinition(Behavior):
    isParallel: bool

    do_action_id: Optional[str]
    entry_action_id: Optional[str]
    exit_action_id: Optional[str]

    @staticmethod
    def from_dict(data) -> StateDefinition:
        do_action_id = get_optional_id(data, "doAction")
        entry_action_id = get_optional_id(data, "entryAction")
        exit_action_id = get_optional_id(data, "exitAction")

        return StateDefinition(
            id=get_string(data, "@id"),
            type_=get_string(data, "@type"),
            owner_id=get_optional_id(data, "owner"),
            name=get_string(data, "name"),
            qualified_name=get_string(data, "qualifiedName"),
            do_action_id=do_action_id,
            entry_action_id=entry_action_id,
            exit_action_id=exit_action_id,
            isParallel=get_bool(data, "isParallel"),
        )

from __future__ import annotations

from dataclasses import dataclass

from sysml_code_generator.mapper.conversions import (
    get_list_of_ids,
    get_optional_id,
    get_string,
)
from sysml_code_generator.model.sysml.expression import Expression


@dataclass
class OperatorExpression(Expression):
    argumentIds: list[str]
    operator: str
    outputIds: list[str]
    inputIds: list[str]

    @staticmethod
    def from_dict(data) -> OperatorExpression:
        return OperatorExpression(
            id=get_string(data, "@id"),
            type_=get_string(data, "@type"),
            owner_id=get_optional_id(data, "owner"),
            name=get_string(data, "name"),
            qualified_name=get_string(data, "qualifiedName"),
            argumentIds=get_list_of_ids(data, "argument"),
            operator=get_string(data, "operator"),
            inputIds=get_list_of_ids(data, "input"),
            outputIds=get_list_of_ids(data, "output"),
        )

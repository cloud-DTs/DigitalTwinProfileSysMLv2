from __future__ import annotations

from dataclasses import dataclass

from sysml_code_generator.mapper.conversions import (
    get_id,
    get_list_of_ids,
    get_optional_id,
    get_string,
)
from sysml_code_generator.model.sysml.expression import Expression


@dataclass
class FeatureChainExpression(Expression):
    # 8.3.4.8.3 FeatureChainExpression

    # 8.4.4.9.5 Operator Expressions
    # The performance of the Function '.' then results in the effective chaining of the value of its source parameter
    # (which will be the result of the argument Expression of the FeatureChainExpression) and the
    # source::target Feature (which will be the targetFeature of the FeatureChainExpression).

    target_feature_id: str
    # SPEC: is feature
    # REALITY: ReferenceUsage from SysML - fucks with typing, sad for programmer
    # TODO: maybe analyze further and write this down

    argument_ids: list[str]

    @staticmethod
    def from_dict(data) -> FeatureChainExpression:
        return FeatureChainExpression(
            id=get_string(data, "@id"),
            type_=get_string(data, "@type"),
            owner_id=get_optional_id(data, "owner"),
            name=get_string(data, "name"),
            qualified_name=get_string(data, "qualifiedName"),
            target_feature_id=get_id(data, "targetFeature"),
            argument_ids=get_list_of_ids(data, "argument"),
        )

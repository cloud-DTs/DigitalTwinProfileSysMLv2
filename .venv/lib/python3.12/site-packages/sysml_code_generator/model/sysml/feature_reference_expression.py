from __future__ import annotations

from dataclasses import dataclass

from sysml_code_generator.mapper.conversions import get_id, get_optional_id, get_string
from sysml_code_generator.model.sysml.expression import Expression


@dataclass
class FeatureReferenceExpression(Expression):
    referent_id: str

    @staticmethod
    def from_dict(data) -> FeatureReferenceExpression:
        return FeatureReferenceExpression(
            id=get_string(data, "@id"),
            type_=get_string(data, "@type"),
            owner_id=get_optional_id(data, "owner"),
            name=get_string(data, "name"),
            qualified_name=get_string(data, "qualifiedName"),
            referent_id=get_id(data, "referent"),
        )

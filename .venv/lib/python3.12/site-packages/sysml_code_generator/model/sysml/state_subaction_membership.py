from __future__ import annotations

from dataclasses import dataclass

from sysml_code_generator.mapper.conversions import get_id, get_optional_id, get_string
from sysml_code_generator.model.sysml.sysml_entity import SysMLEntity


@dataclass
class StateSubactionMembership(SysMLEntity):
    kind: str
    owned_member_feature_id: str

    @staticmethod
    def from_dict(data) -> StateSubactionMembership:
        return StateSubactionMembership(
            id=get_string(data, "@id"),
            type_=get_string(data, "@type"),
            owner_id=get_optional_id(data, "owner"),
            name=get_string(data, "name"),
            qualified_name=get_string(data, "qualifiedName"),
            kind=get_string(data, "kind"),
            owned_member_feature_id=get_id(data, "ownedMemberFeature"),
        )

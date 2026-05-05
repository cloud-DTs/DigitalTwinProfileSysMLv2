from __future__ import annotations

from dataclasses import dataclass

from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.mapper.conversions import (
    get_list_of_ids,
    get_optional_id,
    get_string,
)
from sysml_code_generator.model.sysml.sysml_entity import SysMLEntity


@dataclass
class AttributeUsage(SysMLEntity):
    data_type_ids: list[str]

    @staticmethod
    def from_dict(data) -> AttributeUsage:
        return AttributeUsage(
            id=get_string(data, "@id"),
            type_=get_string(data, "@type"),
            owner_id=get_optional_id(data, "owner"),
            name=get_string(data, "name"),
            qualified_name=get_string(data, "qualifiedName"),
            data_type_ids=get_list_of_ids(data, "type"),
        )

    # TODO: duplication with reference_usage
    def get_first_data_type(self, repository: RepositoryInterface):
        if len(self.data_type_ids) == 0:
            raise ValueError(f"Attribute has no datatype! {self.qualified_name}")

        data_type_id = self.data_type_ids[0]

        data_type = repository.get(item_id=data_type_id)

        if data_type.qualified_name == "":
            raise ValueError("Invalid Data Type.")

        return data_type.qualified_name

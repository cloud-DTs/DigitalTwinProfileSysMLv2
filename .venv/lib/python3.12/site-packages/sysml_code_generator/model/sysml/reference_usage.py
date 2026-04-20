from __future__ import annotations

from dataclasses import dataclass

from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.mapper.conversions import (
    get_list_of_ids,
    get_optional_id,
    get_string,
)
from sysml_code_generator.model.sysml.data_type import DataType
from sysml_code_generator.model.sysml.sysml_entity import SysMLEntity


@dataclass
class ReferenceUsage(SysMLEntity):
    data_type_ids: list[str]

    @staticmethod
    def from_dict(data) -> ReferenceUsage:
        return ReferenceUsage(
            id=get_string(data, "@id"),
            type_=get_string(data, "@type"),
            owner_id=get_optional_id(data, "owner"),
            name=get_string(data, "name"),
            qualified_name=get_string(data, "qualifiedName"),
            data_type_ids=get_list_of_ids(data, "type"),
        )

    def is_data_type(
        self, repository: RepositoryInterface, qualified_name: str
    ) -> bool:
        for data_type_id in self.data_type_ids:
            data_type = repository.get(item_id=data_type_id)

            if not isinstance(data_type, DataType):
                raise ValueError("Unexpected Type.")

            if data_type.qualified_name == qualified_name:
                return True

        return False

    def get_first_data_type(
        self, repository: RepositoryInterface
    ):  # TODO: check if this ok (to just take first)
        # TODO: doesn't work with syson
        data_type_id = self.data_type_ids[0]
        data_type = repository.get(item_id=data_type_id)

        if data_type.qualified_name == "":
            raise ValueError("Invalid Data Type.")

        return data_type.qualified_name

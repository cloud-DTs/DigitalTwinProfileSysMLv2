from typing import Optional

from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.sysml.sysml_entity import SysMLEntity


class Repository(RepositoryInterface):
    __itemsById: dict[str, SysMLEntity]

    def __init__(
        self,
    ) -> None:
        self.__itemsById = {}

    def add_item(self, item: object):
        if not isinstance(item, SysMLEntity):
            raise ValueError("Invalid Element.")

        if item.id in self.__itemsById:
            raise ValueError(f"Element with this ID already present: {item.id}")

        self.__itemsById[item.id] = item

    def get_all(self) -> list[SysMLEntity]:
        return list(self.__itemsById.values())

    def get(self, item_id: str) -> SysMLEntity:
        if item_id in self.__itemsById:
            return self.__itemsById[item_id]

        raise RuntimeError(
            f"Item not found: {item_id}. "
            f"Item might be of unsupported type or standard element."
        )

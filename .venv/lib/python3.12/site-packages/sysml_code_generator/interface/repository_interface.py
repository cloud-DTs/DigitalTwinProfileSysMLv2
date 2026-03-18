from typing import Protocol

from sysml_code_generator.model.sysml.sysml_entity import SysMLEntity


class RepositoryInterface(Protocol):
    def get(self, item_id: str) -> SysMLEntity: ...

    def get_all(self) -> list[SysMLEntity]: ...

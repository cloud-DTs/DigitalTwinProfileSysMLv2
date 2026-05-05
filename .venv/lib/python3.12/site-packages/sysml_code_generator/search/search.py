from typing import Optional

from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.sysml.sysml_entity import SysMLEntity


class Search:
    def __init__(
        self,
        repository: RepositoryInterface,
    ):
        self.__repository = repository

    def get_by_qualified_name(self, qualified_name: str) -> Optional[SysMLEntity]:
        results = []

        for item in self.__repository.get_all():
            if item.qualified_name == qualified_name:
                results.append(item)

        number_of_results = len(results)

        if number_of_results == 0:
            return None

        if number_of_results > 1:
            raise ValueError(
                "Expected qualified name to be unique, two elements found."
            )

        return results[0]

    def get_by_type_and_owner_id(
        self,
        type_: str,
        owner_id: str,
    ):
        results = []

        for item in self.__repository.get_all():
            if item.type_ == type_:
                if item.owner_id == owner_id:
                    results.append(item)

        return results

    def get_by_type(
        self,
        type_: str,
    ):
        results = []

        for item in self.__repository.get_all():
            if item.type_ == type_:
                results.append(item)

        return results

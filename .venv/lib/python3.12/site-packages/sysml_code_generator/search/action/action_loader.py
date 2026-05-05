from sysml_code_generator.loader.repository import Repository
from sysml_code_generator.model.generator.action_data import ActionData
from sysml_code_generator.search.search import Search


class ActionLoader:
    __repository: Repository
    __search: Search

    def __init__(
        self,
        repository: Repository,
        search: Search,
    ):
        self.__repository = repository
        self.__search = search

    def load(
        self,
        qualified_name: str,
    ) -> ActionData:
        action = self.__search.get_by_qualified_name(qualified_name=qualified_name)

        if action is None:
            raise ValueError(f"State machine {qualified_name} not found.")

        owned_actions = self.__search.get_by_type_and_owner_id(
            type_="ActionUsage",
            owner_id=action.id,
        )

        steps = owned_actions  # TODO: replace

        return ActionData(
            name=action.name,
            steps=steps,
        )

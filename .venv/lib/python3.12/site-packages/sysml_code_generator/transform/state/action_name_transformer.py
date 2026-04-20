from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.sysml.action_usage import ActionUsage


class ActionNameTransformer:
    def __init__(
        self,
        repository: RepositoryInterface,
    ):
        self.__repository = repository

    def transform(
        self,
        action_id: str,
    ) -> str:
        action = self.__repository.get(action_id)

        if action is None:
            raise ValueError(f"Action not found: {action_id}")

        if not isinstance(action, ActionUsage):
            type_ = type(action)
            raise ValueError(f"Unexpected Type for action {action_id}: {type_}")

        transformed_name = action.name

        return transformed_name

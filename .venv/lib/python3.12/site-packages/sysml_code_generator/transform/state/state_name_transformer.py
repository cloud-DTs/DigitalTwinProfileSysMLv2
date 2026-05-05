from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.sysml.action_usage import ActionUsage
from sysml_code_generator.model.sysml.state_usage import StateUsage


class StateNameTransformer:
    def __init__(
        self,
        repository: RepositoryInterface,
    ):
        self.__repository = repository

    def transform(
        self,
        state_id: str,
    ) -> str:
        action = self.__repository.get(state_id)

        if action is None:
            raise ValueError(f"State not found: {state_id}")

        if not isinstance(action, StateUsage):
            type_ = type(action)
            raise ValueError(f"Unexpected Type for state {state_id}: {type_}")

        transformed_name = action.name

        return transformed_name

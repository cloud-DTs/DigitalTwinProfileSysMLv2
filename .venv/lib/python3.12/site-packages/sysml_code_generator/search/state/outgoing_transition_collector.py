from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.sysml.state_definition import StateDefinition
from sysml_code_generator.model.sysml.state_usage import StateUsage
from sysml_code_generator.model.sysml.transition_usage import TransitionUsage
from sysml_code_generator.search.search import Search


class OutgoingTransitionCollector:
    def __init__(
        self,
        repository: RepositoryInterface,
        search: Search,
    ):
        self.__repository = repository
        self.__search = search

    def collect(
        self,
        state_usage: StateUsage,
    ) -> list[TransitionUsage]:
        state_machine = self.__repository.get(state_usage.owner_id)

        if not isinstance(state_machine, (StateUsage, StateDefinition)):
            type_ = type(state_machine)
            raise ValueError(
                f"Owner of state is not a stat machine. Owner {state_usage.owner_id}, Type: {type_}."
            )

        all_transitions = self.__search.get_by_type_and_owner_id(
            type_="TransitionUsage",
            owner_id=state_machine.id,
        )

        result = []

        for transition in all_transitions:
            if not isinstance(transition, TransitionUsage):
                type_ = type(transition)
                raise ValueError(
                    f"Expected element to be of type TransitionUsage. {type_}"
                )

            if transition.source_id == state_usage.id:
                result.append(transition)

        return result

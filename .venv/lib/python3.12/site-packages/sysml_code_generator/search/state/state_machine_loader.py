from typing import Union

from sysml_code_generator.exception.unsupported_model_error import UnsupportedModelError
from sysml_code_generator.loader.repository import Repository
from sysml_code_generator.model.generator.state_machine_data import StateMachineData
from sysml_code_generator.model.sysml.state_definition import StateDefinition
from sysml_code_generator.model.sysml.state_usage import StateUsage
from sysml_code_generator.search.search import Search
from sysml_code_generator.search.state.get_initial_state import get_initial_state


class StateMachineLoader:
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
    ):
        state_machine = self.__search.get_by_qualified_name(
            qualified_name=qualified_name,
        )

        if not isinstance(state_machine, (StateDefinition, StateUsage)):
            raise ValueError(
                "Expected element to be a State Machine: " + qualified_name
            )

        if state_machine is None:
            raise ValueError(f"State machine {qualified_name} not found.")

        if state_machine.isParallel is True:
            raise UnsupportedModelError("Parallel state machines are not supported.")

        states = self.__search.get_by_type_and_owner_id(
            type_="StateUsage",
            owner_id=state_machine.id,
        )

        transitions = self.__search.get_by_type_and_owner_id(
            type_="TransitionUsage",
            owner_id=state_machine.id,
        )

        initial_state = get_initial_state(
            state_machine=state_machine,
            repository=self.__repository,
            search=self.__search,
        )

        if not isinstance(initial_state, StateUsage):
            raise Exception(f"Unexpected type of initial state.")

        return StateMachineData(
            name=state_machine.name,
            states=states,
            transitions=transitions,
            entryState=initial_state,
            repository=self.__repository,
        )

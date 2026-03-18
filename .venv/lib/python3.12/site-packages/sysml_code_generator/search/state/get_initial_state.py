from typing import Union

from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.sysml.state_definition import StateDefinition
from sysml_code_generator.model.sysml.state_usage import StateUsage
from sysml_code_generator.search.search import Search
from sysml_code_generator.search.transition_usage.search_entry_transition import (
    get_entry_transition,
)


def get_initial_state(
    state_machine: Union[StateDefinition, StateUsage],
    repository: RepositoryInterface,
    search: Search,
):
    entry_succession = get_entry_transition(
        state_machine=state_machine,
        repository=repository,
        search=search,
    )

    initial_state_id = entry_succession.target_id

    return repository.get(initial_state_id)

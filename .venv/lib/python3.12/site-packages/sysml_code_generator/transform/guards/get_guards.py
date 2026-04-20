from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.sysml.expression import Expression
from sysml_code_generator.model.sysml.transition_usage import TransitionUsage
from sysml_code_generator.search.transition_usage.guard_collector import (
    get_guards as search_get_guards,  # TODO: naming
)


def get_guards(
    transitions: list[TransitionUsage],
    repository: RepositoryInterface,
) -> list[Expression]:
    guards_by_id = {}

    for transition in transitions:
        guards = search_get_guards(
            transition_usage=transition,
            repository=repository,
        )

        for guard in guards:
            if guard.id not in guards_by_id:
                guards_by_id[guard.id] = guard

    return [value for key, value in guards_by_id.items()]

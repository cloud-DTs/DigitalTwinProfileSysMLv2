from sysml_code_generator.exception.unsupported_model_error import UnsupportedModelError
from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.sysml.perform_action_usage import PerformActionUsage
from sysml_code_generator.model.sysml.state_usage import StateUsage
from sysml_code_generator.model.sysml.transition_usage import TransitionUsage
from sysml_code_generator.search.transition_usage.get_actions import (
    get_transition_effect_actions,
)


def get_actions_by_id_from_transitions(
    transitions: list[TransitionUsage],
    states: list[StateUsage],
    repository: RepositoryInterface,
) -> dict[str, PerformActionUsage]:
    actions_by_id = {}
    action_ids = set()

    for transition in transitions:
        actions = get_transition_effect_actions(
            transition_usage=transition,
            repository=repository,
        )

        for action in actions:
            if action.id not in actions_by_id:
                action_ids.add(action.id)

    for state in states:
        if state.entry_action_id is not None:
            action_ids.add(state.entry_action_id)
        if state.do_action_id is not None:
            action_ids.add(state.do_action_id)
        if state.exit_action_id is not None:
            action_ids.add(state.exit_action_id)

    for action_id in action_ids:
        action = repository.get(action_id)

        if not isinstance(action, PerformActionUsage):
            raise UnsupportedModelError(
                "Expected transition effect to be of type PerformActionUsage."
            )

        actions_by_id[action_id] = action

    return actions_by_id

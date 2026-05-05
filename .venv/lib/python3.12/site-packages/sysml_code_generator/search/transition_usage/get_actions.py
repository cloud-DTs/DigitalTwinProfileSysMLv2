from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.sysml.action_usage import ActionUsage
from sysml_code_generator.model.sysml.transition_usage import TransitionUsage


def get_transition_effect_actions(
    transition_usage: TransitionUsage,
    repository: RepositoryInterface,
) -> list[ActionUsage]:
    actions = []

    for effect_id in transition_usage.effect_action_ids:
        action = repository.get(item_id=effect_id)

        if not isinstance(action, ActionUsage):
            raise ValueError(
                "Expected transition effect to be of type PerformActionUsage."
            )

        actions.append(action)

    return actions

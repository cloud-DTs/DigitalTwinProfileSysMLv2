from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.sysml.action_usage import ActionUsage
from sysml_code_generator.model.sysml.perform_action_usage import PerformActionUsage


def get_actions_from_performance(
    actions_by_id: dict[str, PerformActionUsage],
    repository: RepositoryInterface,
) -> list[ActionUsage]:
    action_usage_ids = set()
    action_usages = []

    for action_id in actions_by_id:
        performed_action_usage = actions_by_id[action_id]

        action_usage_id = performed_action_usage.perform_action_usage_id
        action_usage_ids.add(action_usage_id)

    for action_usage_id in action_usage_ids:
        action_usage = repository.get(action_usage_id)

        if not isinstance(action_usage, ActionUsage):
            type_ = type(action_usage)
            raise ValueError(
                f"Expected element to be of type ActionUsage: {action_usage_id} {type_}"
            )

        action_usages.append(action_usage)

    return action_usages

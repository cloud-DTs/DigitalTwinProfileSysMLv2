from sysml_code_generator.model.generator.state_machine_data import StateMachineData
from sysml_code_generator.transform.state.action_name_transformer import (
    ActionNameTransformer,
)


class ActionNameCollector:
    def __init__(
        self,
        action_name_transformer: ActionNameTransformer,
    ):
        self.__action_name_transformer = action_name_transformer

    def collect_action_names(
        self,
        state_machine_data: StateMachineData,
    ) -> list[str]:

        action_ids = set()
        action_names = (
            set()
        )  # do to references there might be multiple ActionUsages for the same action

        for transition_usage in state_machine_data.transitions:
            for action_id in transition_usage.effect_action_ids:
                action_ids.add(action_id)

        for action_id in action_ids:
            action_name = self.__action_name_transformer.transform(
                action_id=action_id,
            )

            action_names.add(action_name)

        action_names_list = list(action_names)
        action_names_list.sort()

        return action_names_list

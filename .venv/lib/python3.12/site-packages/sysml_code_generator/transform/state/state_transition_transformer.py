from sysml_code_generator.exception.unsupported_model_error import UnsupportedModelError
from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.sysml.action_usage import ActionUsage
from sysml_code_generator.model.sysml.state_usage import StateUsage
from sysml_code_generator.model.sysml.transition_usage import TransitionUsage
from sysml_code_generator.model.template.state_c.transition import Transition
from sysml_code_generator.search.state.outgoing_transition_collector import (
    OutgoingTransitionCollector,
)
from sysml_code_generator.transform.state.action_name_transformer import (
    ActionNameTransformer,
)
from sysml_code_generator.transform.state.condition_transformer import (
    ConditionTransformer,
)
from sysml_code_generator.transform.state.state_name_transformer import (
    StateNameTransformer,
)


class StateTransitionTransformer:
    def __init__(
        self,
        condition_transformer: ConditionTransformer,
        state_name_transformer: StateNameTransformer,
        action_name_transformer: ActionNameTransformer,
        outgoing_transition_collector: OutgoingTransitionCollector,
        repository: RepositoryInterface,
    ):
        self.__condition_transformer = condition_transformer
        self.__state_name_transformer = state_name_transformer
        self.__action_name_transformer = action_name_transformer
        self.__outgoing_transition_collector = outgoing_transition_collector
        self.__repository = repository

    def transform_transitions_of_state(
        self,
        state: StateUsage,
    ) -> list[Transition]:
        all_transitions: list[TransitionUsage]
        outgoing_transitions = self.__outgoing_transition_collector.collect(
            state_usage=state
        )

        transformed_transitions = []

        for transition_usage in outgoing_transitions:
            if transition_usage.trigger_action_ids:
                raise UnsupportedModelError(
                    "Trigger conditions for State Transitions are not supported."
                )

            target = self.__repository.get(transition_usage.target_id)

            if isinstance(target, ActionUsage) and (
                target.qualified_name == "Actions::Action::done"
            ):
                continue

            source_name = self.__state_name_transformer.transform(
                transition_usage.source_id
            )
            target_name = self.__state_name_transformer.transform(
                transition_usage.target_id
            )

            effect_names = []

            for effect_id in transition_usage.effect_action_ids:
                effect_name = self.__action_name_transformer.transform(
                    action_id=effect_id
                )
                effect_names.append(effect_name)

            condition = self.__condition_transformer.transform(
                transition=transition_usage,
            )

            transition = Transition(
                previous=source_name,
                next=target_name,
                condition=condition,
                effects=effect_names,
            )

            transformed_transitions.append(transition)

        return transformed_transitions

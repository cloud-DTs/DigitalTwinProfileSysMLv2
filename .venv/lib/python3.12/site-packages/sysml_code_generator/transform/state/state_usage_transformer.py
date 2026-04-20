from typing import Optional, Tuple

from sysml_code_generator.exception.unsupported_model_error import UnsupportedModelError
from sysml_code_generator.model.sysml.state_usage import StateUsage
from sysml_code_generator.model.template.state_c.state import State
from sysml_code_generator.model.template.state_c.transition import Transition
from sysml_code_generator.transform.state.action_name_transformer import (
    ActionNameTransformer,
)
from sysml_code_generator.transform.state.state_transition_transformer import (
    StateTransitionTransformer,
)


class StateUsageTransformer:
    def __init__(
        self,
        transition_transformer: StateTransitionTransformer,
        action_name_transformer: ActionNameTransformer,
    ):
        self.__action_name_transformer = action_name_transformer
        self.__transition_transformer = transition_transformer

    def transform_state_usage(
        self,
        state: StateUsage,
        enum: int,
    ) -> State:
        do_action = None

        if state.entry_action_id:
            raise UnsupportedModelError("Entry actions are not supported.")
        if state.exit_action_id:
            raise UnsupportedModelError("Exit actions are not supported.")

        if state.do_action_id:
            do_action = self.__action_name_transformer.transform(
                action_id=state.do_action_id,
            )

        transitions = self.__transition_transformer.transform_transitions_of_state(
            state=state,
        )

        conditional_transitions, unconditional_transition = (
            self.__split_default_transition(
                transitions=transitions,
                state=state,
            )
        )

        state = State(
            name=state.name,
            enum=enum,
            do_action=do_action,
            conditional_transitions=conditional_transitions,
            default_transition=unconditional_transition,
        )

        return state

    def __split_default_transition(
        self,
        transitions: list[Transition],
        state: StateUsage,
    ) -> Tuple[list[Transition], Optional[Transition]]:
        # ensure there is only one default transition, and it is at the end
        unconditional_transition = None
        conditional_transitions = []
        for transition in transitions:
            if len(transition.condition) == 0:
                if unconditional_transition is not None:
                    raise UnsupportedModelError(
                        f"Found more then one unconditional transition for state {state.name}"
                    )

                unconditional_transition = transition
            else:
                conditional_transitions.append(transition)

        return conditional_transitions, unconditional_transition

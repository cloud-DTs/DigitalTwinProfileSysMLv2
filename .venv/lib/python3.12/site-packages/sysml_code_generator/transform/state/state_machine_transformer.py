from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.generator.state_machine_data import StateMachineData
from sysml_code_generator.model.template.state_c.state_variables import StateVariables
from sysml_code_generator.tool.validate_c_name import validate_c_name
from sysml_code_generator.transform.state.collect_actions_from_state import (
    ActionNameCollector,
)
from sysml_code_generator.transform.state.collect_variables_from_state import (
    VariableCollector,
)
from sysml_code_generator.transform.state.state_name_transformer import (
    StateNameTransformer,
)
from sysml_code_generator.transform.state.state_usage_transformer import (
    StateUsageTransformer,
)


class StateMachineTransformer:
    def __init__(
        self,
        repository: RepositoryInterface,
        state_usage_transformer: StateUsageTransformer,
        state_name_transformer: StateNameTransformer,
        action_name_collector: ActionNameCollector,
        variable_collector: VariableCollector,
    ):
        self.__repository = repository
        self.__state_usage_transformer = state_usage_transformer
        self.__state_name_transformer = state_name_transformer
        self.__action_name_collector = action_name_collector
        self.__variable_collector = variable_collector

    def transform(
        self,
        state_machine_data: StateMachineData,
    ) -> StateVariables:
        state_machine_data.sort()
        enum = 0

        transformed_states = []

        for state_data in state_machine_data.states:
            transformed_state = self.__state_usage_transformer.transform_state_usage(
                state=state_data,
                enum=enum,
            )

            enum += 1
            transformed_states.append(transformed_state)

        initial_state_name = self.__state_name_transformer.transform(
            state_machine_data.entryState.id
        )

        action_names = self.__action_name_collector.collect_action_names(
            state_machine_data=state_machine_data,
        )

        variables = self.__variable_collector.collect_variables(
            state_machine_data=state_machine_data,
        )

        state_variables = StateVariables(
            name=state_machine_data.name,
            variables=variables,
            action_names=action_names,
            states=transformed_states,
            initial_state_name=initial_state_name,
        )

        self.validate(
            state_variables=state_variables,
        )

        return state_variables

    def validate(
        self,
        state_variables: StateVariables,
    ) -> None:
        for variable in state_variables.variables:
            validate_c_name(variable.name)

        for action_name in state_variables.action_names:
            validate_c_name(action_name)

        for state in state_variables.states:
            validate_c_name(state.name)

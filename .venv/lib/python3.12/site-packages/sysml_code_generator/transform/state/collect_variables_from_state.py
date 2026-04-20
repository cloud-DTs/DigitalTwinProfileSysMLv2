from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.generator.state_machine_data import StateMachineData
from sysml_code_generator.model.sysml.expression import Expression
from sysml_code_generator.model.template.state_c.variable import Variable
from sysml_code_generator.transform.expressions.variable_to_template import (
    c_operand_variable,
)
from sysml_code_generator.transform.guards.get_guard_variables import (
    get_guard_variables,
)
from sysml_code_generator.transform.state.map_data_type import map_data_type


class VariableCollector:
    def __init__(
        self,
        repository: RepositoryInterface,
    ):
        self.__repository = repository

    def collect_variables(
        self,
        state_machine_data: StateMachineData,
    ) -> list[Variable]:
        variables = []
        guards = []

        for transition in state_machine_data.transitions:
            for guard_id in transition.guard_expression_ids:
                guard = self.__repository.get(guard_id)

                if not isinstance(guard, Expression):
                    type_ = type(Expression)
                    raise ValueError(
                        f"Expected guard to by of type Expression. {guard_id} {type_}"
                    )

                guards.append(guard)

        for variable in get_guard_variables(
            guards=guards,
            repository=self.__repository,
        ):
            variable_data = Variable(
                name=c_operand_variable(variable),
                data_type=map_data_type(variable.data_type),
                data_type_sysml=variable.data_type,
            )

            variables.append(variable_data)

        return variables

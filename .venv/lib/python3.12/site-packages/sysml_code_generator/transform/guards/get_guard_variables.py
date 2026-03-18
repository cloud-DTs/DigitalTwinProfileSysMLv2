from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.generator.guard.operand import Operand
from sysml_code_generator.model.sysml.expression import Expression
from sysml_code_generator.transform.guards.flatten import flatten
from sysml_code_generator.transform.guards.get_expression_parts import (
    get_expression_parts,
)


def get_guard_variables(
    guards: list[Expression], repository: RepositoryInterface
) -> list[Operand]:
    variables_by_name = {}
    variables = []

    for guard in guards:
        deep_parts = get_expression_parts(expression=guard, repository=repository)

        expression_parts = flatten(deep_parts)

        for part in expression_parts:
            if isinstance(part, Operand):
                if part.name not in variables_by_name:
                    variables_by_name[part.name] = part

    for variable_name in variables_by_name:
        variables.append(variables_by_name[variable_name])

    return variables

from typing import Union

from sysml_code_generator.model.generator.guard.operand import Operand
from sysml_code_generator.model.generator.guard.operator import Operator
from sysml_code_generator.model.generator.guard.part import ExpressionPart
from sysml_code_generator.transform.expressions.operator import supported_operators
from sysml_code_generator.transform.expressions.variable_to_template import (
    c_operand_variable,
)


def c_join(
    parts: Union[ExpressionPart, list[ExpressionPart]],
    level: int = 0,
) -> str:
    parts_joined = []
    level_next = level + 1

    if not isinstance(parts, list):  # REFACTOR
        parts = [parts]

    for part in parts:
        if isinstance(part, list):
            joined = c_join(part, level_next)
            parts_joined.append(joined)
        elif isinstance(part, Operator):
            if part.name not in supported_operators:
                raise ValueError(f"Operator {part.name} not supported.")

            c_operator = supported_operators[part.name]
            parts_joined.append(c_operator)
        elif isinstance(part, Operand):
            c_name = c_operand_variable(part)
            parts_joined.append(c_name)
        else:
            raise ValueError()

    result = " ".join(parts_joined)

    # codestyle workaround for unary operator
    result = result.replace("! ", "!")

    return result

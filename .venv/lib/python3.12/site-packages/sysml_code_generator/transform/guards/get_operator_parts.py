from typing import Union

from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.generator.guard.operator import Operator
from sysml_code_generator.model.sysml.operator_expression import OperatorExpression
from sysml_code_generator.model.sysml.sysml_entity import SysMLEntity


def get_operator_parts(
    expression: OperatorExpression,
    repository: RepositoryInterface,
) -> list[Union[Operator, SysMLEntity]]:
    element_index = {
        "x": None,
        "y": None,
        "firstValue": None,
        "secondValue": None,
    }

    for input_id in expression.inputIds:
        input_ = repository.get(item_id=input_id)
        name = input_.name

        if name not in element_index:
            raise ValueError(f"Unexpected OperatorExpression input type: {name}")

        if element_index[name] is not None:
            raise ValueError(f"Duplicated OperatorExpression input type: {name}")

        element_index[name] = input_

    operator = expression.operator

    if expression.operator in ["and", "or"]:
        first_value = element_index.get("firstValue")
        second_value = element_index.get("secondValue")

        if first_value is None:
            raise ValueError("Operator expression: first value missing.")

        if second_value is None:
            raise ValueError("Operator expression: second value missing.")

        return [first_value, Operator(operator), second_value]
    elif expression.operator in [">", ">=", "<", "<=", "==", "!="]:
        x = element_index.get("x")
        y = element_index.get("y")

        if x is None:
            raise ValueError("Operator expression: x value missing.")

        if y is None:
            raise ValueError("Operator expression: y value missing.")

        return [x, Operator(operator), y]
    elif expression.operator in ["not"]:
        x = element_index.get("x")

        if x is None:
            raise ValueError("Operator expression: x value missing.")

        return [Operator(operator), x]
    else:
        raise RuntimeError(f"Operator '{expression.operator}' not implemented.")

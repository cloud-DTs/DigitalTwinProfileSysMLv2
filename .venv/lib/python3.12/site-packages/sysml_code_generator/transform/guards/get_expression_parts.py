from typing import Union

from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.generator.guard.part import ExpressionPart
from sysml_code_generator.model.sysml.attribute_usage import AttributeUsage
from sysml_code_generator.model.sysml.feature import Feature
from sysml_code_generator.model.sysml.feature_chain_expression import (
    FeatureChainExpression,
)
from sysml_code_generator.model.sysml.feature_reference_expression import (
    FeatureReferenceExpression,
)
from sysml_code_generator.model.sysml.operator_expression import OperatorExpression
from sysml_code_generator.model.sysml.reference_usage import ReferenceUsage
from sysml_code_generator.model.sysml.sysml_entity import SysMLEntity
from sysml_code_generator.transform.guards.get_operand_from_feature_chain import (
    get_operand_from_feature_chain,
)
from sysml_code_generator.transform.guards.get_operand_part import get_operand_part
from sysml_code_generator.transform.guards.get_operator_parts import get_operator_parts
from sysml_code_generator.transform.guards.resolve_reference import resolve_if_reference


def get_expression_parts(
    expression: Union[ExpressionPart, SysMLEntity], repository: RepositoryInterface
) -> list[Union[ExpressionPart, SysMLEntity]]:
    processed_parts = []

    # Operand
    if isinstance(expression, AttributeUsage):
        parts = [get_operand_part(expression, repository)]
    elif isinstance(expression, ReferenceUsage):
        parts = [get_operand_part(expression, repository)]
    elif isinstance(expression, FeatureChainExpression):
        # TODO: reconsider treating dot as an operator
        parts = [get_operand_from_feature_chain(expression, repository)]
    # Operator + Operand
    elif isinstance(expression, OperatorExpression):
        parts = get_operator_parts(expression, repository)
    # follow references
    elif isinstance(expression, Feature):
        parts = [resolve_if_reference(expression, repository)]
    elif isinstance(expression, FeatureReferenceExpression):
        parts = [resolve_if_reference(expression, repository)]
    else:
        raise NotImplementedError(
            f"Can not produce OperatorExpression parts for type: '{expression.type_}'."
        )

    # recurse until whole tree is mapped to operators and operands
    for part in parts:
        if isinstance(part, ExpressionPart):
            processed_parts.append(part)
        else:
            recursively_processed_parts = get_expression_parts(
                expression=part,
                repository=repository,
            )

            for recursively_processed_part in recursively_processed_parts:
                processed_parts.append(recursively_processed_part)

    return processed_parts

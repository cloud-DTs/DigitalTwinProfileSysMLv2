from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.sysml.expression import Expression
from sysml_code_generator.transform.expressions.join_expression import c_join
from sysml_code_generator.transform.guards.get_expression_parts import (
    get_expression_parts,
)

# TODO: encapsule generator specific transformations


class GuardCTransformer:
    def __init__(
        self,
        repository: RepositoryInterface,
    ):
        self.__repository = repository

    def transform(
        self,
        guard: Expression,
    ) -> str:

        expression_parts = get_expression_parts(
            expression=guard, repository=self.__repository
        )

        c_expression = c_join(expression_parts)

        return c_expression

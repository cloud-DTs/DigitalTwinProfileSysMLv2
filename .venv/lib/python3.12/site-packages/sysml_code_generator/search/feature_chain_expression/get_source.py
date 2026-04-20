from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.sysml.feature_chain_expression import (
    FeatureChainExpression,
)
from sysml_code_generator.model.sysml.feature_reference_expression import (
    FeatureReferenceExpression,
)


def get_source(
    feature_chain_expression: FeatureChainExpression, repository: RepositoryInterface
) -> FeatureReferenceExpression:
    source = repository.get(feature_chain_expression.argument_ids[0])

    if not isinstance(source, FeatureReferenceExpression):
        raise ValueError(
            "Expected feature chain expression source to be of type FeatureReferenceExpression."
        )

    return source

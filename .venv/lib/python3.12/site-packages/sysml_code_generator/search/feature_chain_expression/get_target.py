from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.sysml.feature_chain_expression import (
    FeatureChainExpression,
)
from sysml_code_generator.model.sysml.reference_usage import ReferenceUsage


def get_target(
    feature_chain_expression: FeatureChainExpression, repository: RepositoryInterface
) -> ReferenceUsage:
    target = repository.get(feature_chain_expression.target_feature_id)

    if not isinstance(target, ReferenceUsage):
        raise ValueError("Expected Target to be of type ReferenceUsage")

    return target

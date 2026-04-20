from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.sysml.feature_reference_expression import (
    FeatureReferenceExpression,
)


def get_referent(
    feature_reference_expression: FeatureReferenceExpression,
    repository: RepositoryInterface,
):
    return repository.get(
        item_id=feature_reference_expression.referent_id,
    )

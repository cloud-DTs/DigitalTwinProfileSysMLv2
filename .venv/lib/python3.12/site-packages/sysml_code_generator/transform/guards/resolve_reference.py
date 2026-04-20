from typing import Union

from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.sysml.feature import Feature
from sysml_code_generator.model.sysml.feature_chain_expression import (
    FeatureChainExpression,
)
from sysml_code_generator.model.sysml.feature_reference_expression import (
    FeatureReferenceExpression,
)
from sysml_code_generator.model.sysml.sysml_entity import SysMLEntity
from sysml_code_generator.search.feature.get_element import get_element
from sysml_code_generator.search.feature_reference_expression.get_referent import (
    get_referent,
)


def resolve_if_reference(
    element: SysMLEntity,
    repository: RepositoryInterface,
) -> SysMLEntity:
    if isinstance(element, Feature):
        element = get_element(
            feature=element,
            repository=repository,
        )
    elif isinstance(element, FeatureReferenceExpression):
        element = get_referent(
            feature_reference_expression=element,
            repository=repository,
        )
        # e.g. operator expression
    elif isinstance(element, FeatureChainExpression):
        element = element.get_target(repository)

    return element

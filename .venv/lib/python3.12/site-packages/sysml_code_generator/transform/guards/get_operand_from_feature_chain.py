from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.generator.guard.operand import Operand
from sysml_code_generator.model.sysml.feature_chain_expression import (
    FeatureChainExpression,
)
from sysml_code_generator.model.sysml.reference_usage import ReferenceUsage
from sysml_code_generator.search.feature_chain_expression.get_source import get_source
from sysml_code_generator.search.feature_chain_expression.get_target import get_target
from sysml_code_generator.search.feature_reference_expression.get_referent import (
    get_referent,
)


def get_operand_from_feature_chain(
    feature_chain: FeatureChainExpression,
    repository: RepositoryInterface,
) -> Operand:
    # TODO: multi chain

    source = get_source(
        feature_chain_expression=feature_chain,
        repository=repository,
    )  # FeatureReferenceExpression

    target = get_target(
        feature_chain_expression=feature_chain,
        repository=repository,
    )  # ReferenceUsage

    referent = get_referent(
        feature_reference_expression=source,
        repository=repository,
    )

    if not isinstance(referent, ReferenceUsage):
        raise NotImplementedError()

    data_type = target.get_first_data_type(repository)

    return Operand(name=target.name, data_type=data_type, path=[referent.name])

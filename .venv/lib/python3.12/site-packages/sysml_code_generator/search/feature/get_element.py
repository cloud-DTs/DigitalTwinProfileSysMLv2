from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.sysml.feature import Feature
from sysml_code_generator.model.sysml.sysml_entity import SysMLEntity


def get_element(
    feature: Feature,
    repository: RepositoryInterface,
) -> SysMLEntity:
    if len(feature.owned_element_ids) == 0:
        raise ValueError("No owned element.")

    if len(feature.owned_element_ids) > 1:
        raise ValueError("Expected single owned element.")

    member = repository.get(feature.owned_element_ids[0])

    return member

from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.sysml.state_subaction_membership import (
    StateSubactionMembership,
)


def get_action(
    state_subaction_membership: StateSubactionMembership,
    repository: RepositoryInterface,
):
    member = repository.get(state_subaction_membership.owned_member_feature_id)

    return member

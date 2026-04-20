from typing import Optional, Union

from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.sysml.state_definition import StateDefinition
from sysml_code_generator.model.sysml.state_usage import StateUsage
from sysml_code_generator.model.sysml.succession_as_usage import SuccessionAsUsage
from sysml_code_generator.model.sysml.transition_usage import TransitionUsage
from sysml_code_generator.search.search import Search


def get_entry_transition(
    search: Search,
    repository: RepositoryInterface,
    state_machine: Union[StateDefinition, StateUsage],
) -> Optional[Union[TransitionUsage, SuccessionAsUsage]]:
    entry_action_id = state_machine.entry_action_id

    if not entry_action_id:
        return None

    transition_usages = search.get_by_type(
        type_="TransitionUsage",
    )

    entry_transition_ids = []

    for transition_usage in transition_usages:
        succession_id = transition_usage.id

        if transition_usage.source_id == entry_action_id:
            entry_transition_ids.append(succession_id)

    if len(entry_transition_ids) > 1:
        raise ValueError("Expected only one entry transition, found multiple.")

    dummy_transition = None
    if len(entry_transition_ids) == 0:
        # try with succession
        dummy_transition = try_with_succession(
            search=search,
            entry_action_id=entry_action_id,
        )

    if len(entry_transition_ids) == 0 and dummy_transition is None:
        raise ValueError("Entry succession not found.")

    if len(entry_transition_ids) > 0:
        entry_transition = repository.get(item_id=entry_transition_ids[0])
    else:
        entry_transition = dummy_transition

    if not isinstance(entry_transition, TransitionUsage):
        raise ValueError("Expected Entry Transition to be of type TransitionUsage")

    return entry_transition


def try_with_succession(
    search: Search,
    entry_action_id: str,
) -> Optional[TransitionUsage]:
    dummy_transitions = []

    # REFACTOR: work with features of state machine
    succession_usages = search.get_by_type(
        type_="SuccessionAsUsage",
    )

    for succession_usage in succession_usages:
        for source_id in succession_usage.source_ids:
            if source_id == entry_action_id:
                # found the entry succession

                if len(succession_usage.source_ids) != 1:
                    raise ValueError(
                        "Expected entry succession to have exactly one source."
                    )

                if len(succession_usage.target_ids) != 1:
                    raise ValueError(
                        "Expected entry succession to have exactly one target."
                    )

                target_id = succession_usage.target_ids[0]

                dummy_transition = TransitionUsage(
                    id="",
                    type_="SuccessionAsUsage",
                    owner_id="",
                    name="",
                    qualified_name="",
                    source_id=source_id,
                    target_id=target_id,
                    guard_expression_ids=[],
                    effect_action_ids=[],
                    trigger_action_ids=[],
                )

                dummy_transitions.append(dummy_transition)

    if len(dummy_transitions) > 1:
        raise ValueError("Expected only one entry succession, found multiple.")

    if len(dummy_transitions) == 0:
        return None

    return dummy_transitions[0]

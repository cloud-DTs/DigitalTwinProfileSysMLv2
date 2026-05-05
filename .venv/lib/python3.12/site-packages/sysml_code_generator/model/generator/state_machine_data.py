from dataclasses import dataclass

from sysml_code_generator.loader.repository import Repository
from sysml_code_generator.model.sysml.state_usage import StateUsage
from sysml_code_generator.model.sysml.transition_usage import TransitionUsage


@dataclass
class StateMachineData:
    name: str
    states: list[StateUsage]
    transitions: list[TransitionUsage]
    entryState: StateUsage
    # TODO: exit state (maybe)
    repository: Repository

    def sort(self):
        self.states.sort(key=lambda state: state.qualified_name)
        self.transitions.sort(
            key=lambda state: state.source_id + "__" + state.target_id
        )

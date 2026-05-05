from dataclasses import dataclass

from sysml_code_generator.model.template.state_c.state import State
from sysml_code_generator.model.template.state_c.variable import Variable


@dataclass
class StateVariables:
    name: str
    variables: list[Variable]
    action_names: list[str]
    states: list[State]
    initial_state_name: str

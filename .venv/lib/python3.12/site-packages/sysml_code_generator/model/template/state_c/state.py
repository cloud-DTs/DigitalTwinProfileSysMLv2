from dataclasses import dataclass
from typing import Optional

from sysml_code_generator.model.template.state_c.transition import Transition


@dataclass
class State:
    name: str
    enum: int
    do_action: Optional[str]
    conditional_transitions: list[Transition]
    default_transition: Optional[Transition]

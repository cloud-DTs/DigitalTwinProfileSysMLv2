from dataclasses import dataclass


@dataclass
class Transition:
    previous: str
    next: str
    condition: str
    effects: list[str]
